from typing import TYPE_CHECKING, Dict, List, Optional

from unified_planning.shortcuts import (
    UserType,
    Object,
    BoolType,
    IntType,
    Fluent,
    InstantaneousAction,
    Problem,
    Or,
    GE,
    LE,
)

from crafting.transformation import Transformation, InventoryOwner
from crafting.task import Task, GetItemTask, PlaceItemTask, GoToZoneTask

if TYPE_CHECKING:
    from crafting.world import World


def world_task_to_planning_problem(
    world: "World", name: str, task: Optional["Task"]
) -> Problem:
    item_type = UserType("item")
    zone_type = UserType("zone")
    player_item_type = UserType("player_item", item_type)
    zone_item_type = UserType("zone_item", item_type)

    zones_obj = {}
    for zone in world.zones:
        zones_obj[zone.name] = Object(zone.name, zone_type)

    items_obj = {}
    for item in world.items:
        items_obj[item.name] = Object(item.name, player_item_type)

    zone_items_obj = {}
    for item in world.zones_items:
        zone_items_obj[item.name] = Object(item.name, zone_item_type)

    pos = Fluent("pos", BoolType(), zone=zone_type)
    amount = Fluent("amount", IntType(), item=player_item_type)
    amount_at = Fluent("amount_at", IntType(), item=zone_item_type, zone=zone_type)

    def add_player_operation(
        action: InstantaneousAction,
        transfo: Transformation,
    ):
        player = InventoryOwner.PLAYER
        add_item_to_quantity = {}
        for stack in transfo.get_changes(player, "add", []):
            stack_amount = amount(items_obj[stack.item.name])
            action.add_increase_effect(stack_amount, stack.quantity)
            add_item_to_quantity[stack.item] = stack.quantity

        for stack in transfo.get_changes(player, "remove", []):
            stack_amount = amount(items_obj[stack.item.name])
            action.add_precondition(GE(stack_amount, stack.quantity))
            action.add_decrease_effect(stack_amount, stack.quantity)

        for max_stack in transfo.get_changes(player, "max", []):
            stack_amount = amount(items_obj[max_stack.item.name])
            removed = add_item_to_quantity.get(max_stack.item, 0)
            action.add_precondition(LE(stack_amount, max_stack.quantity - removed))

    def add_current_zone_operations(
        action: InstantaneousAction, transfo: Transformation, loc
    ):
        current = InventoryOwner.CURRENT
        add_item_to_quantity = {}
        for stack in transfo.get_changes(current, "add", []):
            amount_at_loc = amount_at(zone_items_obj[stack.item.name], loc)
            action.add_increase_effect(amount_at_loc, stack.quantity)
            add_item_to_quantity[stack.item] = stack.quantity

        for rem_stack in transfo.get_changes(current, "remove", []):
            amount_at_loc = amount_at(zone_items_obj[rem_stack.item.name], loc)
            action.add_precondition(GE(amount_at_loc, rem_stack.quantity))
            action.add_decrease_effect(amount_at_loc, rem_stack.quantity)

        for max_stack in transfo.get_changes(current, "max", []):
            amount_at_loc = amount_at(zone_items_obj[max_stack.item.name], loc)
            removed = add_item_to_quantity.get(max_stack.item, 0)
            action.add_precondition(LE(amount_at_loc, max_stack.quantity - removed))

    actions = []
    for t_id, transfo in enumerate(world.transformations):
        action = InstantaneousAction(f"{t_id}_{transfo.name}", loc=zone_type)
        loc = action.parameter("loc")

        action.add_precondition(pos(loc))
        if transfo.zones and world.n_zones > 1:
            action.add_precondition(
                Or(*[pos(zones_obj[zone.name]) for zone in transfo.zones])
            )

        if transfo.destination is not None:
            action.add_effect(pos(loc), False)
            action.add_effect(pos(zones_obj[transfo.destination.name]), True)

        add_player_operation(action, transfo)
        add_current_zone_operations(action, transfo, loc)

        actions.append(action)

    problem = Problem(name)
    problem.add_fluent(pos, default_initial_value=False)
    problem.add_fluent(amount, default_initial_value=0)
    problem.add_fluent(amount_at, default_initial_value=0)
    problem.add_objects(zones_obj.values())
    problem.add_actions(actions)
    if task is not None:
        goal = task_to_goal(
            task, pos, amount, amount_at, items_obj, zone_items_obj, zones_obj
        )
        problem.add_goal(goal)
    for zone_name, zone in zones_obj.items():
        problem.set_initial_value(pos(zone), zone_name == world.start_zone.name)
    for item in items_obj.values():
        problem.set_initial_value(amount(item), 0)
    for zone_item in zone_items_obj.values():
        for zone in zones_obj.values():
            problem.set_initial_value(amount_at(zone_item, zone), 0)

    for stack in world.start_items:
        problem.set_initial_value(amount(items_obj[stack.item.name]), stack.quantity)

    for zone, stacks in world.start_zones_items.items():
        for stack in stacks:
            problem.set_initial_value(
                amount_at(zone_items_obj[stack.item.name], zones_obj[zone.name]),
                stack.quantity,
            )

    return problem


def task_to_goal(
    task: "Task",
    pos: Fluent,
    amount: Fluent,
    amount_at: Fluent,
    items_obj: Dict[str, List[Object]],
    zone_items_obj: Dict[str, List[Object]],
    zones_obj: Dict[str, List[Object]],
):
    if isinstance(task, GetItemTask):
        item = items_obj[task.item_stack.item.name]
        return GE(amount(item), task.item_stack.quantity)
    if isinstance(task, PlaceItemTask):
        item = zone_items_obj[task.item_stack.item.name]
        zone_names = zones_obj.keys()
        if task.zones is not None:
            zone_names = [zone.name for zone in task.zones]
        conditions = [
            GE(amount_at(item, zones_obj[zone_name]), task.item_stack.quantity)
            for zone_name in zone_names
        ]
        return Or(*conditions)
    if isinstance(task, GoToZoneTask):
        return pos(zones_obj[task.zone.name])
    raise NotImplementedError
