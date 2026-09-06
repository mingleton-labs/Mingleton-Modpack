ServerEvents.recipes((event) => {
  // Remove the Builder's Delight Chisel; all recipes now use the Chipped chisel.
  event.remove({ id: "buildersdelight:iron_chisel" });

  // Add custom recipes for golden, rope and copper chains
  event.shaped(Item.of("buildersdelight:chain_1", 1), [" A ", " B ", " A "], {
    A: "minecraft:gold_nugget",
    B: "minecraft:gold_ingot",
  });
  event.shaped(Item.of("buildersdelight:chain_2", 1), [" A ", " A ", " A "], {
    A: "farmersdelight:rope",
  });
  event.shaped(Item.of("buildersdelight:chain_3", 1), [" A ", " B ", " A "], {
    A: "create:copper_nugget",
    B: "minecraft:copper_ingot",
  });

  // Add custom recipes for copper and golden lanterns
  event.shaped(Item.of("buildersdelight:lantern_3", 1), ["AAA", "ABA", "AAA"], {
    A: "create:copper_nugget",
    B: "minecraft:torch",
  });
  event.shaped(Item.of("buildersdelight:lantern_7", 1), ["AAA", "ABA", "AAA"], {
    A: "minecraft:gold_nugget",
    B: "minecraft:torch",
  });
});
