RecipeViewerEvents.removeEntriesCompletely("item", (event) => {
  event.remove({mod: "mysticalagriculture", output:"#c:armors"});
});

ClientEvents.hideJEI(event => {
    // Hides the item from the item panel
    event.hide({mod: "mysticalagriculture", output:"#c:armors"})
})