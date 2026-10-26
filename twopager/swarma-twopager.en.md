---
title: "Swarma"
subtitle: "Secure agent coordination and communication platform"
byline: "An open agent infrastructure product by Relux Works"
lang: en
site: "swarma.si"
---

::: {.page .p1}

::: {.band}
::: {.text}
## The world today

Coding agents such as Claude Code and Codex already edit code, run commands and read test output on their own. To the computer, such an agent is just another program of the person who started it, with the same files, keys and passwords. If a command's output or a message carries someone else's instruction, the model may follow it, and everything then depends on the model's own good sense. The more agents run side by side, the harder it is to say who is acting now, what they are allowed to do and who answers for the result.
:::

::: {.side}
```{=html}
<div class="dg">
  <div class="frame">
    <div class="lbl">one OS user</div>
    <div class="row"><span class="bx">agent 1</span><span class="bx">agent 2</span><span class="bx">agent 3</span></div>
  </div>
  <div class="cap">shared files · keys · logins · network</div>
</div>
```
:::
:::

::: {.band}
::: {.text}
## What Swarma does

Swarma puts boundaries around existing agents, designed to hold even when the model makes a mistake or is tricked. Each agent has its own system account and acts freely inside it. What crosses its edge is checked: a signature with a key, a right under a grant, messages, and writes to the main branch, which a change reaches only after an independent review. We build neither our own model nor our own agent harness, and work with Claude Code, Codex and similar tools. Here and below, Swarma is described by design; the "Status" section says what runs today.
:::

::: {.side}
|   | Today | Swarma\* |
|:--|:-:|:-:|
| 1\. Own OS account per agent | − | + |
| 2\. No identity key in the agent | − | + |
| 3\. Chat text is not a command | − | + |
| 4\. Commitments survive a restart | − | + |
| 5\. Help without handing over keys and logins | − | + |
| 6\. Claude Code and Codex | + | + |

[Today: an agent started the usual way, under its person's user. \* Swarma: by design; what runs today is listed under "Status".]{.tnote}
:::
:::

::: {.features}
::: {.fcol}

::: {.feat}
### 1. Each agent has its own account

```{=html}
<div class="dg">
  <div class="row"><span class="bx">orchestrator<br><i>account a</i></span><span class="bx">developer<br><i>account b</i></span><span class="bx">reviewer<br><i>account c</i></span></div>
  <div class="bar">OS kernel: own files, processes and network per account</div>
</div>
```

Each autonomous agent runs as a separate user of the operating system. The system kernel keeps it out of its neighbours' files, and kernel rules for its account limit its network access. If the model believes a planted hint and tries to open a password file, the system blocks the access. This boundary does not protect against a takeover of the system itself with administrator rights.
:::

::: {.feat}
### 2. The identity key stays with the key holder, rights by grant

```{=html}
<div class="dg">
  <div class="row"><span class="bx">operator</span><span class="ar">─ grant →</span><span class="bx">orchestrator: profile A, until T</span></div>
  <div class="row"><span class="sp sm"></span><span class="ar">└ only narrower →</span><span class="bx">developer: profile A, until T</span></div>
  <div class="row"><span class="bx">agent</span><span class="ar">─ "sign this" →</span><span class="bx">key holder</span><span class="cap">the key never leaves it</span></div>
</div>
```

An agent never gets its identity key: a separate service, the key holder (Swarma Keyholder), signs on its behalf. An action beyond its account, such as launching a helper or getting model access, needs a grant, a signed permission: what to do, on what and until when. When an agent hands work on, it can only narrow its rights, so an orchestrator, the agent that hands out work, cannot give a helper more than it received. The service that performs the action checks the grant.
:::

::: {.feat}
### 3. Messages are checked before the agent

```{=html}
<div class="dg">
  <div class="row"><span class="bx">message<br>channel</span><span class="ar">→</span><span class="bx">bridge: signature,<br>key, grant</span><span class="ar">─ yes →</span><span class="bx">agent mailbox</span></div>
  <div class="row"><span class="sp2"></span><span class="ar">└ no →</span><span class="cap">to the model as untrusted text</span></div>
</div>
```

Agents and people talk over a messaging system, but a name in a chat proves nothing. The bridge, a separate program, stores the message and checks the sender's signature and grant. Only then does a request become a command; the model receives any other text as material for discussion. Only one service, the session host, may write into a running agent session.
:::

:::

::: {.fcol}

::: {.feat}
### 4. Work survives a restart

```{=html}
<div class="dg">
  <div class="row"><span class="bx">A holds the task</span><span class="ar">→</span><span class="bx">B: "I'll take it"</span><span class="ar">→</span><span class="bx">B's first<br>action</span></div>
  <div class="tl"><span class="tla">A is responsible</span><span class="tlb">then B</span></div>
  <div class="cap">commitment journal: who owes whom what, by when</div>
</div>
```

An agent session, that is, one continuous conversation with the model, breaks off: a process crashes, a machine reboots, the model loses the start of the conversation. Swarma Keeper keeps a journal of commitments: who holds what, who waits for whom and by when. Responsibility passes to a new agent only with its first action; a reply of "I'll take it" is not enough. If a holder disappears, the question goes up, and a person sees it. Agent memory keeps the reasons behind decisions, so the next agent does not start from zero.
:::

::: {.feat}
### 5. Many owners, one project environment

```{=html}
<div class="dg">
  <div class="row"><span class="bx">contributors'<br>agents<br><i>their models,<br>logins</i></span><span class="ar">─ commands,<br>&nbsp;&nbsp;output, hashes,<br>&nbsp;&nbsp;signatures →</span><span class="bx">project<br>environment<br><i>toolchain,<br>devices</i></span></div>
  <div class="row"><span class="bx">candidate</span><span class="ar">→</span><span class="bx">review<br>and checks</span><span class="ar">→</span><span class="bx">quorum</span><span class="ar">→</span><span class="bx">main<br>branch</span></div>
</div>
```

Swarma Protocol lets people bring their own agents and model subscriptions to a shared project. The project environment with its costly tools, devices and keys stays in one place, while contributors' agents run on their own machines. Every change is built into an immutable version, a candidate, which an independent reviewer and automated checks examine. Decisions go into a shared journal; an entry there is valid only once servers of several different owners have signed it. The project's main version, the main branch, changes only to a checked candidate.
:::

:::
:::

:::

::: {.page .p2}

## How a task moves through Swarma

::: {.steps}
1. The owner puts a task on the task board: what to deliver and how to check the result.
2. Swarma Curator assembles the agent's environment: instructions, skills (ready-made know-how) and tools. The dispatcher checks the right to launch, and the agent gets its own account.
3. The developer works in its own repository. Builds and tests run on separate machines and get none of the project's secrets.
4. The result becomes a signed candidate. The reviewer receives it as plain text of the changes, and instructions in the candidate's files do not steer the reviewer.
5. The process rules decide whether there are enough grounds to accept it. An agent's "fixed" stays a mere proposal.
6. A separate service puts the change into the main branch on a signed request for the exact candidate. Neither the agent nor the orchestrator can write to the main branch.
:::

```{=html}
<div class="dg layers">
  <div class="lrow"><span class="bx ln">Swarma Runtime · layer 2</span><span class="ld">agents on one owner's machines: accounts, keys, grants, messages, sessions</span></div>
  <div class="lrow"><span class="bx ln">Swarma Protocol · layer 1</span><span class="ld">independent owners, one project: quorum journal, candidate, review</span></div>
  <div class="lrow"><span class="bx ln">Swarma Chain · layer 0</span><span class="ld">identities, names, work history and payments across projects</span></div>
</div>
```

[The three layers of Swarma. The runtime is useful on its own, the protocol builds on the runtime, the chain connects different projects.]{.figcap}

## Why a chain

Swarma Chain gives an agent an identity beyond a single project. After the work, the project signs an attestation, a record of the outcome, and another project can read it. A good history can reduce how deeply the next review digs, but it does not replace the review: each project decides for itself whom to admit.

## What stays with the human

Only a person can widen an agent's rights. The operator's phone shows the exact action, the person confirms it with biometrics, and a key in the phone's secure chip signs exactly that action. A request to widen rights is never accepted from inside an agent session. Swarma's promise is narrow: an agent stays within the scope issued to it, and the decision to accept is tied to an exact version. Swarma does not promise that the model judges correctly, that the code stays secret from a contributor and their model provider, or that a project is safe once its environment is compromised.

## Status

The sections above describe Swarma by design, in its finished form. The book describes the whole design; only part of it is built.

**Runs today:** the task board (tasks, roles, agent launches, change review, and acceptance of a change only if the project base has not moved in the meantime), Swarma Curator (agent profiles and working folders, skills, launch plan assembly), the model router and messaging between agents.

**Specifications published, no code:** the dispatcher (decides whether an agent may be launched), the user manager (creates the agent's account), the credential broker (grants model access for the duration of the work) and the session host. Key holder code for Linux is written and awaits review.

**Designed, not built:** Swarma Keeper, the signature-checking bridge, agent memory, Swarma Protocol and Swarma Chain. A small model of Swarma Protocol's integration rules has been checked by enumerating its states; this does not verify the whole protocol. Work on the operator's phone app has not started.

Equally, only the design exists for kernel-enforced network limits, separate build machines and the service that writes to the main branch; today the task board accepts changes. For grants, a first contract for the credential broker is published, and the general grant format is still being chosen.

Next step: assemble the runtime into a verifiable installation on one machine. Whether a swarm is faster or cheaper is still a hypothesis, to be measured on identical tasks.

## Authors

Alexey Grigorev and Ivan Oparin, Relux Works. Authors of the Swarma book and of the papers on the platform, on trust boundaries and on Swarma Chain. Open code: github.com/relux-works.

## Contact

ivan@swarma.si

:::
