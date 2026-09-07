ServerEvents.recipes((event) => {
    event.remove({ mod: "create", output: "create:andesite_alloy" });
    event.shapeless(Item.of('kubejs:crushed_andesite', 2),
        [
            'immersiveengineering:hammer',
            '4x minecraft:andesite'
        ]);
    event.shaped(Item.of('kubejs:wet_andesite_pile', 4),
        [
            "DAC",
            "ABA",
            "CAD"
        ],
        {
            A: 'kubejs:crushed_andesite',
            B: 'minecraft:water_bucket',
            C: 'farmersdelight:canvas',
            D: 'minecraft:iron_nugget'
        });
    event.smelting('create:andesite_alloy', 'kubejs:wet_andesite_pile');
    event.blasting('create:andesite_alloy', 'kubejs:wet_andesite_pile');
    event.recipes.create.mixing('kubejs:crushed_andesite', '4x minecraft:andesite');
});