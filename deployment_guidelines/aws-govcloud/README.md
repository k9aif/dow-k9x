# Sample deployment guideline: DAS on AWS GovCloud (US)

Status: sample reference architecture, 2026-10-29. Not an authorization package. Items marked
**(verify)** depend on authorizations or DoD guidance that change; confirm them against the sources at
the end before design decisions are made.

## 1. Target and assumptions

| Item | Choice | Why |
|---|---|---|
| Cloud | **AWS GovCloud (US)**, two regions (US-West primary, US-East for recovery) | FedRAMP High and DoD CC SRG IL4/IL5 authorized, US-person operated, isolated from the commercial regions |
| Impact level | **IL4** for Controlled Unclassified Information (requirement and acquisition documents are usually CUI); **IL5** if the mission owner categorises the data or mission higher | DAS itself is unclassified. IL6 (SECRET) is out of scope: it needs the AWS Secret Region, not GovCloud |
| Compute | **Containers on Amazon EKS** (FedRAMP High in GovCloud since 2021) | The router, orchestrators and app backend are already containers (Podman today) |
| Users | DoW staff on the DoD Information Network (DoDIN/NIPRNet), signing in with CAC/PKI | No public internet access, unlike das.k9x.ai |

FedRAMP has moved to a class naming in which "High" is reported as **Class D** **(verify)**; this guide
says "FedRAMP High".

## 2. Connecting on-premises DoW networks to GovCloud

Your instinct is right that AWS Direct Connect is the private link, but for IL4 and IL5 it is **not
enough on its own**. DoD policy requires commercial cloud at IL4 and above to connect to the DoDIN
through a **DISA Boundary Cloud Access Point (BCAP)**: the DISN Enterprise Cloud Access Point, or a
Component CAP approved by the DoW CIO (waiver authority: DoW CIO) **(verify)**.

```
DoW users (CAC) ─► DoDIN / NIPRNet ─► DISA BCAP (Enterprise or approved Component CAP)
                                          │  DISN transport or secure leased line
                                          ▼
                      AWS Direct Connect (GovCloud) ─► Direct Connect gateway
                                          │
                                          ▼
                    Transit account: Transit Gateway ─► inspection VPC (VDSS)
                                          │                AWS Network Firewall / third-party via
                                          │                Gateway Load Balancer, WAF, logging
                                          ▼
                    Workload account: DAS VPC (private subnets only, three Availability Zones)
```

This follows the DoD **Secure Cloud Computing Architecture (SCCA)**, which has four parts:

| SCCA part | What it does | AWS building blocks |
|---|---|---|
| **BCAP** | Protects the DISN from the cloud; connects the cloud to the DoDIN | DISA-operated; reached over Direct Connect |
| **VDSS** (Virtual Datacenter Security Stack) | Inspects and filters traffic into and out of the mission VPCs | Inspection VPC: AWS Network Firewall or a vendor firewall behind Gateway Load Balancer, AWS WAF, VPC Flow Logs |
| **VDMS** (Virtual Datacenter Managed Services) | Patching, scanning, logging, identity services for the workloads | Systems Manager, Inspector, GuardDuty, Security Hub, CloudTrail, centralised logging account |
| **TCCM** (Trusted Cloud Credential Manager) | Controls who holds privileged cloud credentials | IAM Identity Center with CAC-backed federation, separate break-glass process |

AWS's **Landing Zone Accelerator** (with its DoD/SCCA configuration) builds much of this account and
network structure **(verify current version)**. Use separate accounts for transit, logging, security
tooling, and each DAS environment (dev, test, prod).

Two practical points:

- Order **redundant Direct Connect** links at two locations; the BCAP connection and its approval take
  time, so start the DISN connection process early.
- **No internet egress** from workload subnets. AWS services are reached through VPC endpoints
  (PrivateLink); container images come from Amazon ECR inside GovCloud; use the FIPS endpoints.

## 3. Mapping DAS components to AWS

| DAS today (Podman on one host) | On GovCloud | Notes |
|---|---|---|
| **App backend** (FastAPI web UI and API, job dispatcher) | EKS Deployment behind an **internal** Application Load Balancer | Reached only from the DoDIN through the BCAP and VDSS. See section 5 before running more than one replica |
| **Router** (`dow_router_process`, Kafka consumer) | EKS Deployment | Stateless; scale replicas up to the partition count of its inbound topic |
| **Orchestrators** (`dow_orchestrator_process`: requirement, MDD package, MSA, TMRR runs) | EKS Deployment, scaled by **KEDA** on Kafka consumer lag | Long-running LLM stages; scale on lag, not CPU |
| Kafka | **Amazon MSK** (FedRAMP High in GovCloud), TLS and IAM authentication | One topic per run, as today; key messages by job id so a job's events stay in order |
| Job queue (ElasticMQ, SQS-compatible) | **Amazon SQS** FIFO | Same API; the code already uses an SQS client |
| Object storage (MinIO) | **Amazon S3** with SSE-KMS, VPC endpoint, bucket policies; **Object Lock** for gate decision records | Object Lock gives the "decisions are immutable" control (DAS-CTL-004) in storage |
| PostgreSQL with pgvector (knowledge corpus, HIL) | **Amazon RDS for PostgreSQL** or **Aurora PostgreSQL** with the pgvector extension, Multi-AZ | **(verify)** pgvector availability for the chosen engine version in GovCloud |
| Neo4j (requirements traceability graph) | Neo4j on EKS or EC2 (self-managed), or **Amazon Neptune** (openCypher) | Neptune needs query changes and testing; self-managed Neo4j keeps the code unchanged |
| LLM, Granite Guardian, embeddings (Ollama on one RTX 5090) | **Self-hosted on GPU nodes** in EKS (vLLM or Ollama on g6e/g5/p5 instances), **or Amazon Bedrock** models approved at the required level | Bedrock in GovCloud lists models approved for FedRAMP High and IL4/5, varying by model **(verify per model)**. Keep the grader (judge) a different model family from the generator |
| Docling-Serve (document conversion, OCR) | EKS Deployment (CPU, or GPU for heavy OCR) | Internal service only |
| K9X HIL (gate decisions) | Its own EKS Deployment and RDS PostgreSQL | Same network; decision authorities sign in with CAC |
| `.env` secrets | **AWS Secrets Manager** with KMS, injected by the External Secrets Operator or the Secrets Store CSI driver | Nothing secret in images or the repository |
| Logs and metrics | CloudWatch; Amazon Managed Service for Prometheus and Managed Grafana (both report FedRAMP High in GovCloud, 2026) | Feed the VDMS logging account |

## 4. Identity and access

The demonstration uses local logins and leaves some endpoints open on purpose
([`docs/design/authentication-and-demo-scope.md`](../../docs/design/authentication-and-demo-scope.md)).
A DoW deployment changes that:

1. **CAC/PKI sign-in** through the organisation's identity provider (OIDC/SAML). K9-AIF includes an
   OIDC authenticator (`k9_aif_abb/k9_security/zero_trust/oidc_authenticator.py`).
2. **Sign-in required on every API endpoint**, including job submission.
3. **Zero Trust identity on every event:** the API calls K9-AIF `BaseRouter.admit()` with the signed-in
   user, which removes any caller-supplied identity fields and adds an HMAC-signed identity
   (`K9_IDENTITY_SECRET` from Secrets Manager); set `enable_zero_trust: true` so every router and
   orchestrator verifies it.
4. **Named decision authorities:** set `DAS_HIL_APPROVERS` (or the IdP group behind it) per gate.
5. **Workload identity:** each Kubernetes service account gets its own IAM role (IRSA or EKS Pod
   Identity) with least privilege: the router reads and writes MSK topics only; orchestrators also read
   and write their S3 prefixes; only the app backend sends to SQS.

## 5. Scaling out

| Component | Scales as is? | How |
|---|---|---|
| Router | **Yes** | More replicas in the same consumer group, up to the topic's partition count |
| Orchestrators | **Yes**, with more GPU capacity | KEDA on consumer lag of the run topics; each replica needs model capacity, so scale the GPU pool (or Bedrock throughput) with it |
| LLM serving | **Yes** | vLLM replicas on a GPU node group with Cluster Autoscaler or Karpenter; or Bedrock |
| App backend | **No, not yet** | It holds jobs (`_job_store`), live event streams (`_sse_clients`), the single-flight dispatcher state and grading state **in memory**. Run **one replica** until these move to shared stores |
| Single-flight dispatch | **By design, one job at a time** | Protects one GPU in the demo. With a GPU pool, allow N concurrent jobs |

Code changes needed before the app backend can run several replicas:

1. Move the job store, pipeline store and grading state to PostgreSQL (or DynamoDB), keyed by job id.
2. Fan out live events through a shared channel (a Kafka results topic consumer per replica, or
   ElastiCache for Redis pub/sub) instead of the in-process client list.
3. Make dispatch concurrency a setting (default 1) and take jobs from SQS with a visibility timeout, so
   any replica (or a separate dispatcher Deployment) can run it.
4. Then: HorizontalPodAutoscaler on the app backend, and a PodDisruptionBudget on every Deployment.

The `DAS_INSTANCE` setting already lets two DAS deployments share Kafka, storage and the queue with
separate topics, groups and prefixes; it can separate environments or tenants in one cluster.

## 6. Resilience

- Three Availability Zones for EKS nodes, MSK brokers and RDS (Multi-AZ).
- S3 versioning and Object Lock; cross-region replication to US-East for recovery.
- RDS automated backups and snapshots copied to the recovery region; Neo4j backups to S3.
- Failures already propagate in DAS (a failed model call ends the stage as a recorded error with Retry),
  so a lost pod does not produce partial output; Kafka consumer groups resume from the last committed
  offset.
- Recovery objectives (RTO/RPO) are the mission owner's to set.

## 7. Build and release

- Build images from hardened bases: DoD **Iron Bank** (Platform One) images, or STIG-hardened images.
- Scan in the pipeline (Amazon Inspector for ECR, plus the organisation's scanner); sign images and
  enforce signatures at admission.
- Push to Amazon ECR in GovCloud; deploy by GitOps (Argo CD or Flux) from an internal repository.
- Infrastructure as code (Terraform or CloudFormation / Landing Zone Accelerator), reviewed and
  versioned with the application.
- Before each release: the K9-AIF Inspector (`k9aif inspect`) and the DAS tests, as today.

## 8. Authorization path

1. Data categorisation and impact level (IL4 or IL5) with the mission owner.
2. System Security Plan and the RMF package (DoDI 8510.01), inheriting AWS GovCloud's FedRAMP High and
   CC SRG IL4/5 controls from the AWS authorization package.
3. DISN connection approval and BCAP connection (DISA).
4. Authority to Operate from the Authorizing Official; continuous monitoring after.

## 9. Sample manifests

[`kubernetes/`](kubernetes/) holds sample manifests for the three DAS processes: the app backend
(one replica, internal load balancer), the router (consumer group, scaled replicas) and the
orchestrators (KEDA on Kafka lag). Values in `<angle brackets>` are placeholders.

[`architecture.puml`](architecture.puml) is the deployment diagram (PlantUML; rendered: [`architecture.png`](architecture.png)).

## Sources (checked 2026-10-29)

- AWS, [Amazon Bedrock models get FedRAMP High and DoD IL-4/5 approval in AWS GovCloud (US)](https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-bedrock-models-fedramp-high-dod-il-4-5-govcloud/) (May 2025)
- AWS, [OpenAI GPT, OpenAI GPT OSS, and NVIDIA Nemotron models on Amazon Bedrock receive FedRAMP High and DoD IL-4/5 approval in AWS GovCloud (US)](https://aws.amazon.com/about-aws/whats-new/2026/06/addl-bedrock-model-fedramp-il-5-govcloud/) (June 2026)
- AWS, [Amazon Managed Service for Prometheus achieves FedRAMP High and DoD IL-4/5 authorization in AWS GovCloud (US)](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-managed-service-prometheus-fedramp-high/) (July 2026)
- AWS, [Amazon EKS is now FedRAMP-High compliant](https://aws.amazon.com/about-aws/whats-new/2021/04/amazon-eks-is-now-fedramp-high-compliant/) (2021)
- AWS, [Amazon MSK is now FedRAMP compliant](https://aws.amazon.com/about-aws/whats-new/2022/06/amazon-managed-streaming-apache-kafka-fedramp-compliant) (2022; FedRAMP High in GovCloud)
- AWS, [FedRAMP compliance](https://aws.amazon.com/compliance/fedramp/) and [GovCloud (US) newsletter](https://aws.amazon.com/govcloud-us/newsletter/newsletter-issue-05/)
- AWS Prescriptive Guidance, [Secure architecture for DoD workloads](https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/secure-architecture-dod/secure-architecture-dod.pdf); AWS Public Sector blog, [How to implement CNAP for federal and DoD customers in AWS](https://aws.amazon.com/blogs/publicsector/how-implement-cnap-federal-dod-customers-aws/)
- DoD CIO, [Cloud Security Playbook, Volume 1](https://dodcio.defense.gov/Portals/0/Documents/Library/CloudSecurityPlaybookVol1.pdf) (Feb 2025): IL4 and above connect through the DISN Enterprise CAP or a DoD CIO-approved Component CAP
- DISA, [Secure Cloud Computing Architecture](https://disa.mil/~/media/Files/DISA/News/Events/secure-cloud-computing-architecture-121117.pdf); [SCCA functional requirements](https://rmf.org/wp-content/uploads/2025/05/DoD-Secure-Cloud-Computing-Architecture-Functional-Requirements.pdf)

Not confirmed from primary sources for this guide: the current CC SRG revision and DISN Connection
Process Guide text, FedRAMP's class naming, pgvector support per GovCloud database engine, and IL5
status for each individual service. Check them before relying on this.
