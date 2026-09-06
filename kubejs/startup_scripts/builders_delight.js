// Take the Iron Chisel out of the creative menu. The Chipped chisel replaces it.
//
// Startup scripts do not reload with /reload. Restart the game after editing.

["blocks", "decoration", "materials"].forEach((tab) => {
  StartupEvents.modifyCreativeTab(`buildersdelight:${tab}`, (event) => {
    event.remove("buildersdelight:iron_chisel");
  });
});
