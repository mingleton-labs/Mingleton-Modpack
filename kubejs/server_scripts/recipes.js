ServerEvents.recipes((event) => {
  console.log("Hello! Recipes");

  // Test chisel
  event.custom({
    type: "chipped:chisel",
    tags: ["chipped:obsidian"],
    primary_product: {
      item: "minecraft:obsidian",
    },
    results: [
      { item: "minecraft:obsidian" },
      { item: "minecraft:crying_obsidian" },
    ],
  });
});
