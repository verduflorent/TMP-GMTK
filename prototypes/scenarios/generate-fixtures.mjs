// P0-01: deterministic, framework-independent narrative graph fixtures.
// Run: node prototypes/scenarios/generate-fixtures.mjs
import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = dirname(fileURLToPath(import.meta.url));
const kinds = ["narration", "interpretation", "splash", "gm_note", "transition", "encounter"];
const sizes = { S: [50, 100], M: [200, 400], L: [500, 1000] };
function rng(seed) {
  let state = seed >>> 0;
  return () => ((state = (Math.imul(state, 1664525) + 1013904223) >>> 0) / 4294967296);
}
export function makeFixture(sceneCount, transitionCount, seed = 20261009) {
  if (sceneCount < 12 || transitionCount < 12) throw Error("Fixture too small");
  const random = rng(seed);
  const scenes = Array.from({ length: sceneCount }, (_, i) => ({
    id: `scene-${String(i + 1).padStart(4, "0")}`,
    title: i % 9 === 0 ? `Scène ${i + 1} — Réunion à l'observatoire, décision imprévue` : `Scène ${i + 1} — Écho`,
    narrative_order: i,
    position: { x: Math.round((i % 20) * 280 + random() * 35), y: Math.round(Math.floor(i / 20) * 185 + random() * 35) },
    rubric_types: i % 11 === 0 ? [] : Array.from({ length: i % 7 }, (_, j) => kinds[j]),
    rubric_count: i % 11 === 0 ? 0 : i % 7 + (i % 5 === 0 ? 1 : 0),
  }));
  // Reserve the last scene as an intentionally disconnected scene.
  const edges = [
    [0, 1], [1, 2], [2, 0], // cycle
    [3, 3], // self-loop
    [4, 5], [4, 5], // parallel
    [6, 8], [7, 8], // convergence
    [9, 10], [9, 11], [9, 12], [9, 13], [9, 14], // 5 exits
  ];
  while (edges.length < transitionCount) {
    const source = Math.floor(random() * (sceneCount - 1));
    const target = Math.floor(random() * (sceneCount - 1));
    edges.push([source, target]);
  }
  const transitions = edges.map(([a, b], i) => ({
    id: `transition-${String(i + 1).padStart(5, "0")}`,
    source: scenes[a].id,
    target: scenes[b].id,
    label: `Vers ${scenes[b].title}`,
  }));
  return { fixture_version: 1, seed, scenes, transitions };
}
export function validateFixture(data, expectedScenes, expectedTransitions) {
  const { scenes, transitions } = data;
  if (scenes.length !== expectedScenes || transitions.length !== expectedTransitions) throw Error("Incorrect counts");
  const ids = new Set(scenes.map(s => s.id));
  if (ids.size !== scenes.length || new Set(transitions.map(t => t.id)).size !== transitions.length) throw Error("Duplicate IDs");
  if (scenes.some(s => !Number.isFinite(s.position.x) || !Number.isFinite(s.position.y))) throw Error("Invalid coordinates");
  if (transitions.some(t => !ids.has(t.source) || !ids.has(t.target))) throw Error("Dangling transition");
  if (JSON.stringify(JSON.parse(JSON.stringify(data))) !== JSON.stringify(data)) throw Error("Serialization mismatch");
  const has = (a,b) => transitions.some(t => t.source === scenes[a].id && t.target === scenes[b].id);
  if (!(has(0,1) && has(1,2) && has(2,0) && has(3,3))) throw Error("Missing cycle or self-loop");
  if (transitions.filter(t => t.source === scenes[4].id && t.target === scenes[5].id).length < 2) throw Error("Missing parallel edges");
  if (transitions.some(t => t.source === scenes.at(-1).id || t.target === scenes.at(-1).id)) throw Error("Last scene must be isolated");
  if (new Set(transitions.filter(t => t.source === scenes[9].id).map(t => t.target)).size < 5) throw Error("Missing 5-way branch");
  return true;
}
if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  mkdirSync(join(root, "fixtures"), { recursive: true });
  for (const [label, [sceneCount, transitionCount]] of Object.entries(sizes)) {
    const fixture = makeFixture(sceneCount, transitionCount);
    validateFixture(fixture, sceneCount, transitionCount);
    writeFileSync(join(root, "fixtures", label + ".json"), JSON.stringify(fixture, null, 2) + "\n");
    console.log(label + ": " + sceneCount + " scenes / " + transitionCount + " transitions OK");
  }
}
