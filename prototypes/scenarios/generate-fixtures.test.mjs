// P0-01 — vérifications automatisées du contrat de fixtures partagé.
// Exécuter : node --test prototypes/scenarios/generate-fixtures.test.mjs
import test from "node:test";
import assert from "node:assert/strict";
import { makeFixture, validateFixture } from "./generate-fixtures.mjs";

for (const [name, scenes, transitions] of [
  ["S", 50, 100],
  ["M", 200, 400],
  ["L", 500, 1000],
]) {
  test(`fixture ${name} : contrat, invariants et déterminisme`, () => {
    const first = makeFixture(scenes, transitions);
    const second = makeFixture(scenes, transitions);
    assert.deepEqual(first, second);
    assert.equal(validateFixture(first, scenes, transitions), true);
    assert.equal(first.scenes.length, scenes);
    assert.equal(first.transitions.length, transitions);
    assert.deepEqual(JSON.parse(JSON.stringify(first)), first);
    assert.deepEqual(first.scenes.map(s => s.narrative_order), Array.from({ length: scenes }, (_, i) => i));
    assert.ok(first.scenes.some(s => s.rubric_count === 0));
    assert.ok(first.scenes.some(s => s.rubric_count > 0));
    assert.ok(first.scenes.some(s => s.title.includes("—")));
  });
}

test("les tailles incorrectes sont rejetées", () => {
  assert.throws(() => makeFixture(11, 12), /too small/i);
  assert.throws(() => makeFixture(12, 11), /too small/i);
});

test("une transition orpheline est rejetée", () => {
  const fixture = makeFixture(50, 100);
  fixture.transitions[0].target = "scene-inexistante";
  assert.throws(() => validateFixture(fixture, 50, 100), /Dangling transition/);
});

test("une coordonnée invalide est rejetée", () => {
  const fixture = makeFixture(50, 100);
  fixture.scenes[0].position.x = Number.POSITIVE_INFINITY;
  assert.throws(() => validateFixture(fixture, 50, 100), /Invalid coordinates/);
});

test("une collision d'identifiants est rejetée", () => {
  const fixture = makeFixture(50, 100);
  fixture.scenes[1].id = fixture.scenes[0].id;
  assert.throws(() => validateFixture(fixture, 50, 100), /Duplicate IDs/);
});
