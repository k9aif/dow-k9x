# Deployment guidelines

Sample guidance for running DAS (the Defense Acquisition System application, built on K9-AIF) beyond
the public demonstration at das.k9x.ai.

| Guide | Target |
|---|---|
| [`aws-govcloud/`](aws-govcloud/) | AWS GovCloud (US): FedRAMP High, DoD Impact Level 4/5, connected to on-premises Department of War networks; containers on Amazon EKS, scaled out |

These are **reference architectures, not authorization packages**. A real deployment needs the
mission owner's Authority to Operate (ATO) under the DoD Risk Management Framework, the DoD Cloud
Computing Security Requirements Guide (CC SRG) for the chosen impact level, and current guidance from
DISA and the DoW CIO. Cloud authorizations change often: check every service against the current AWS
and FedRAMP listings before relying on this.

How the demonstration itself is secured, and what it leaves open on purpose:
[`docs/design/authentication-and-demo-scope.md`](../docs/design/authentication-and-demo-scope.md).
