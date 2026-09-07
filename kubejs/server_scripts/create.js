ServerEvents.recipes((event) => {
    event.remove({mod: "create", output:"create:andesite_alloy"});
    event.shaped(Item.of('kubejs:crushed_andesite', 4), [
        'AB ',
        'CC ',
        'CC '
    ],
    {
        A: 'immersiveengineering:hammer',
        B: 'minecraft:water_bucket',
        C: 'minecraft:andesite'
    });
});