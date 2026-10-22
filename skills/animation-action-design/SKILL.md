---
name: animation-action-design
description: Design attack animation as readable, timed gameplay with a real body action and synchronized contact events.
---

# Action Design: Attacks, Dodges, Combos and Spellcasting

Summary: Design attack animation as readable, timed gameplay with a real body action and synchronized contact events.
Tags: combat,animation,attacks,combos,game-feel

## Start from player intent
For each move, state the tactical purpose, threat/safety, commitment, effective range, recovery vulnerability, cancel/chain options, hit response and resource cost. Make a timeline before making frames.

## Required timeline
1. **Anticipation:** weight loads, weapon/torch aligns, silhouette makes intent legible.
2. **Initiation:** root/body begins with a visible source of force; no instantaneous pose teleport.
3. **Acceleration:** weapon path builds velocity, torso/shoulder/hip contribute, feet preserve balance.
4. **Contact/release:** define exact gameplay frame and collision/hitbox; synchronize sound and first impact VFX.
5. **Follow-through:** body and weapon continue under momentum; cloth/flame trail responds to movement rather than substituting for it.
6. **Recoil/reaction:** target reaction matches impulse/elemental status; attacker recovers balance or deliberately stays committed.
7. **Recovery/branch:** identify when player regains control, can cancel, can chain, or is punishable.

## Combo design
Record combo state transitions, input buffer window, valid branches, interruption rules, motion direction, root motion, hit-stop budget, hit-confirm behavior and event frame IDs. Avoid one generic animation with different colored particles for all attacks. Each flame should alter movement or contact shape in at least one meaningful way.

## Elemental staging
Make visual elements reinforce an underlying pose/movement event: Blue Jetfire may propel torso/root with thrust direction; Red Blazefire may have a loaded heavy swing and erupting contact; Clear Frostfire may leave a precise freezing plane after a release; Purple Haze may deposit moving volume zones; Green Emeraldfire must show projectile emission and bounce trajectory; Yellow Stormfire must identify charge/arc/target order. No effect may falsify the hitbox or obscure the contact.

## Test matrix
Review close, game camera, dark background, bright background, low-FX/accessibility setting, low frame rate, interrupt/block case, enemy death/hit reaction, player cancellation and final recovery. Log visual and gameplay defects separately.

## Rejection criteria
Reject if anticipation/contact/recovery are indistinct; hands or weapon drift; target hit is not synchronized; VFX hides silhouette; combination window mismatches the pose; the animation is merely image scale/rotation; or one still is reused without intentional design.

## Acceptance criteria
- Anticipation, contact, follow-through, recovery, and combo timing read as distinct full-body action phases.
- Weapon ownership and contact events agree with the gameplay hitbox and target reaction.
- Playback is reviewed at normal and slow speed, with visual and gameplay defects recorded separately.
