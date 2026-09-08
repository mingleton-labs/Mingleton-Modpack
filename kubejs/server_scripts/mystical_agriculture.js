ServerEvents.recipes((event) => {
  event.remove({ mod: "mysticalagriculture", output: "#c:armors" });
  event.remove({ mod: "mysticalagriculture", output: "#c:tools" });

  // Growth accelerators
  event.remove({
    id: "mysticalagriculture:inferium_growth_accelerator",
  });
  event.remove({
    id: "mysticalagriculture:prudentium_growth_accelerator",
  });
  event.remove({
    id: "mysticalagriculture:tertium_growth_accelerator",
  });
  event.remove({
    id: "mysticalagriculture:imperium_growth_accelerator",
  });
  event.remove({
    id: "mysticalagriculture:supremium_growth_accelerator",
  });
  event.remove({
    id: "mysticalagriculture:awakened_supremium_growth_accelerator",
  });
});
