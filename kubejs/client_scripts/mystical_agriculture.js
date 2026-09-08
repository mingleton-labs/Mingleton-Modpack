RecipeViewerEvents.removeEntriesCompletely("item", (event) => {
  // Item entries take an ingredient/predicate, not a recipe filter.
  // Intersect "any item from the mod" with the armor tag.
  event.remove(
    Ingredient.of("@mysticalagriculture").and(Ingredient.of("#c:armors"))
  );

  event.remove(
    Ingredient.of("@mysticalagriculture").and(Ingredient.of("#c:tools"))
  );
});
