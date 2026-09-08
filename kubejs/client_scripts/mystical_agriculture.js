RecipeViewerEvents.removeEntriesCompletely("item", (event) => {
  // Armor & tools
  event.remove(
    Ingredient.of("@mysticalagriculture").and(Ingredient.of("#c:armors")),
  );
  event.remove(
    Ingredient.of("@mysticalagriculture").and(Ingredient.of("#c:tools")),
  );

  // Growth accelerators
  event.remove("mysticalagriculture:inferium_growth_accelerator");
  event.remove("mysticalagriculture:prudentium_growth_accelerator");
  event.remove("mysticalagriculture:tertium_growth_accelerator");
  event.remove("mysticalagriculture:imperium_growth_accelerator");
  event.remove("mysticalagriculture:supremium_growth_accelerator");
  event.remove("mysticalagriculture:awakened_supremium_growth_accelerator");
});
