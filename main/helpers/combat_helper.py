from main.initiative import Initiative, Combatant
import main.data_manager as dm


def obj_to_dict(obj):
    if type(obj) is dict:
        res = {}
        for k, v in obj.items():
            res[k] = obj_to_dict(v)
        return res
    elif type(obj) is list:
        return [obj_to_dict(item) for item in obj]
    elif type(obj) in [Initiative, Combatant]:
        return obj_to_dict(vars(obj))
    else:
        return obj


async def save_combat(ctx, cbt):
    combat_obj = obj_to_dict(cbt) if cbt is not None else None
    dm.save_cached_combat(ctx.guild.id, ctx.channel.id, combat_obj)


async def get_cached_combat(ctx):
    return dm.get_cached_combat(ctx.guild.id, ctx.channel.id)