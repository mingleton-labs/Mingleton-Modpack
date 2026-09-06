// Hide the Iron Chisel and its now-empty category from JEI.
// The Chipped chisel and workbenches cover the same blocks.

RecipeViewerEvents.removeEntriesCompletely("item", (event) => {
  event.remove("buildersdelight:iron_chisel");
});

RecipeViewerEvents.removeCategories((event) => {
  event.remove("buildersdelight:chisel");
});
