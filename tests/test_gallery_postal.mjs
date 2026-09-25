import assert from "node:assert/strict";
import test from "node:test";
import { GALLERY_NODES, resolveGalleryPostal } from "../src/lib/galleryPostal.js";

test("sin parámetro la galería queda en el búnker Oberkampf 75011", () => {
  assert.equal(resolveGalleryPostal(""), "75011");
  assert.equal(GALLERY_NODES["75011"].venue, "BUNKER_OBERKAMPF");
});

test("acepta postal y cp de Lafayette y Marais", () => {
  assert.equal(resolveGalleryPostal("?postal=75009"), "75009");
  assert.equal(resolveGalleryPostal("cp=75004"), "75004");
  assert.equal(resolveGalleryPostal("?postal=75011"), "75011");
});

test("un código desconocido no desplaza el búnker", () => {
  assert.equal(resolveGalleryPostal("?postal=00000"), "75011");
});
