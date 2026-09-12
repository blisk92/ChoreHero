# ADR 0001: Kid identity is the kid device, not an account

- Status: Accepted
- Date: 2026-09-12
- Deciders: Parent (project owner)

## Context

ChoreHero v1 supports exactly one parent and one child per household. The child needs to be able to look at their chores, points, streaks, and request redemptions, but does not need an email, password, or any cross-device identity.

The natural default — borrowed from most apps — is to give the child an account: username, password or PIN, multi-device sessions, the usual. We chose against that for the reasons below.

## Decision

A child has no account. Identity at the kid layer is the **kid device**: each kid device is registered to a specific child profile inside a household and holds a device-scoped session. A child cannot sign in on a new device; a parent must register the new device to the child from their own device using the household QR (or 6-character household code as fallback).

## Consequences

### What this enables

- Zero-authentication friction at the kid layer. No "forgot my password" flows, no PIN rotation, no lost-device lockout that strands a child mid-chore.
- The kid device is a real device-registered thing, which lets us revoke a device from the parent's settings when a tablet is lost or handed off.
- The data model stays flat in v1: one Parent account, one Child profile, N Kid Devices. v2 can layer a second parent account onto the household without touching the kid layer at all.

### What this forecloses

- The child cannot use ChoreHero on a friend's device, a school tablet, or a public computer. v1 only supports devices a parent has registered to the household.
- v2's "second child in the household" requires each child to have their own registered device. Sibling sharing of a device is not supported.
- If we later decide a child should have a portable identity (so they can check their points from anywhere), that's a real lift: child accounts, auth, cross-device sync, and a recovery flow. The ADR becomes the thing future-us argues with.

### What this does **not** foreclose

- A second **parent** account per household. Parents are still account-holders; the "no account for kids" rule does not extend to parents.
- A child having their own auth credentials *behind a parent-controlled switch* later — e.g. for older kids — without rewriting the kid-device model. The device registration stays the source of truth for which child the device belongs to; a child-credentialed login would be an additional, parent-gated layer on top.

## Trade-offs

Alternatives considered:

- **Kid account with username + parent-set PIN.** Most common pattern. Easy for kids, real cross-device portability. Rejected because: (a) cross-device portability is not a v1 need, (b) PIN management is a real failure mode (kids reset, parents forget, devices get passed down with stale PINs), (c) a per-device registration is a simpler data model for v1 and gives parents the safety valve of device revocation.
- **Per-device session tied to the household only, no child profile.** Cheapest model. Rejected because v2 will introduce a second child, and a model that has no child profile at all needs to be retrofitted. Cheap now, expensive later.
- **No kid device, kid uses parent's phone in "switch profile" mode.** Rejected because the parent's phone is rarely in the kid's hands at chore time, and the parent doesn't want their phone passed around.

## Why this is hard to reverse

Adding a child-account layer later without breaking the existing kid-device model is technically possible (see "does not foreclose" above) but it requires every existing kid-device install to be retro-mapped to a new child account, which is the kind of migration that ships with bugs. Not irreversible, but expensive enough that this ADR is worth pinning down.

## Why this is surprising without context

Any developer reading the codebase who sees "kid device registered to household, no kid login" will assume the kid somehow authenticates elsewhere and we're being cute. There is no second layer; the device *is* the identity. That's unusual and warrants the written explanation.
