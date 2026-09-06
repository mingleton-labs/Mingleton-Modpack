// Remove the Builder's Delight Chisel and all its recipes. They are replaced by the Chipped workbenches.

ServerEvents.recipes((event) => {
  event.remove({ id: "buildersdelight:iron_chisel" });
});
