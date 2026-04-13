"""Windowed debug viewer for the current deterministic map pipeline."""

from __future__ import annotations

import math
from dataclasses import dataclass

from rnr_mapgen.colors import (
    BACKGROUND_COLOR,
    GRID_LINE_COLOR,
    HUD_BACKGROUND_COLOR,
    HUD_TEXT_COLOR,
    RIVER_COLOR,
    get_tile_fill_color,
)
from rnr_mapgen.hex import HexCoord
from rnr_mapgen.types import MapData


DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 800
DEFAULT_HEX_RADIUS = 24.0
MIN_ZOOM = 0.5
MAX_ZOOM = 2.5
ZOOM_STEP = 1.15
KEYBOARD_PAN_STEP = 30.0
HUD_HEIGHT = 30
MAP_MARGIN = 64.0

SQRT_3 = math.sqrt(3.0)


@dataclass(slots=True)
class ViewState:
    """Mutable camera state for the debug viewer."""

    offset_x: float
    offset_y: float
    zoom: float = 1.0


def run_viewer(map_data: MapData) -> int:
    """Open a simple interactive debug window for the generated map."""
    try:
        import pygame
    except ImportError as exc:  # pragma: no cover - exercised manually
        raise RuntimeError(
            "Pygame is required for --view. Run `python -m pip install -e .[dev]` to install dependencies."
        ) from exc

    pygame.init()
    pygame.display.set_caption(
        f"RiftandReign Debug Viewer - {map_data.width}x{map_data.height} seed {map_data.seed}"
    )
    screen = pygame.display.set_mode((DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    view_state = make_initial_view_state(map_data, *screen.get_size())
    dragging = False
    last_mouse_position = (0, 0)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    last_mouse_position = event.pos
                elif event.button == 4:
                    zoom_at_screen_position(view_state, event.pos, ZOOM_STEP)
                elif event.button == 5:
                    zoom_at_screen_position(view_state, event.pos, 1.0 / ZOOM_STEP)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                delta_x = event.pos[0] - last_mouse_position[0]
                delta_y = event.pos[1] - last_mouse_position[1]
                view_state.offset_x += delta_x
                view_state.offset_y += delta_y
                last_mouse_position = event.pos

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_LEFT]:
            view_state.offset_x += KEYBOARD_PAN_STEP
        if pressed[pygame.K_RIGHT]:
            view_state.offset_x -= KEYBOARD_PAN_STEP
        if pressed[pygame.K_UP]:
            view_state.offset_y += KEYBOARD_PAN_STEP
        if pressed[pygame.K_DOWN]:
            view_state.offset_y -= KEYBOARD_PAN_STEP
        if pressed[pygame.K_EQUALS] or pressed[pygame.K_PLUS]:
            zoom_at_screen_position(view_state, pygame.mouse.get_pos(), ZOOM_STEP)
        if pressed[pygame.K_MINUS]:
            zoom_at_screen_position(view_state, pygame.mouse.get_pos(), 1.0 / ZOOM_STEP)

        mouse_coord = screen_to_hex_coord(
            map_data=map_data,
            screen_pos=pygame.mouse.get_pos(),
            view_state=view_state,
        )

        draw_map(screen, map_data, view_state, font, mouse_coord)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return 0


def make_initial_view_state(map_data: MapData, window_width: int, window_height: int) -> ViewState:
    """Center the map in the initial window with a small margin."""
    min_x, min_y, max_x, max_y = map_pixel_bounds(map_data, DEFAULT_HEX_RADIUS)
    map_width = max_x - min_x
    map_height = max_y - min_y

    usable_width = max(window_width - (MAP_MARGIN * 2.0), 1.0)
    usable_height = max((window_height - HUD_HEIGHT) - (MAP_MARGIN * 2.0), 1.0)
    zoom = clamp(min(usable_width / map_width, usable_height / map_height, 1.0), MIN_ZOOM, MAX_ZOOM)

    offset_x = ((window_width - (map_width * zoom)) / 2.0) - (min_x * zoom)
    offset_y = (((window_height - HUD_HEIGHT) - (map_height * zoom)) / 2.0) - (min_y * zoom)
    return ViewState(offset_x=offset_x, offset_y=offset_y, zoom=zoom)


def draw_map(screen, map_data: MapData, view_state: ViewState, font, hovered_coord: HexCoord | None) -> None:
    """Draw the visible portion of the map and the optional hover readout."""
    import pygame

    width, height = screen.get_size()
    screen.fill(BACKGROUND_COLOR)
    map_surface_height = max(height - HUD_HEIGHT, 1)
    map_rect = pygame.Rect(0, 0, width, map_surface_height)

    for tile in map_data.tiles.values():
        center_x, center_y = world_to_screen(hex_to_world(tile.coord, DEFAULT_HEX_RADIUS), view_state)
        polygon = hex_polygon_points(center_x, center_y, DEFAULT_HEX_RADIUS * view_state.zoom)
        if not polygon_intersects_rect(polygon, map_rect):
            continue

        pygame.draw.polygon(screen, get_tile_fill_color(tile), polygon)
        pygame.draw.polygon(screen, GRID_LINE_COLOR, polygon, width=1)

    for tile in map_data.tiles.values():
        if not tile.has_river:
            continue

        start_x, start_y = world_to_screen(hex_to_world(tile.coord, DEFAULT_HEX_RADIUS), view_state)
        start_point = (int(round(start_x)), int(round(start_y)))
        line_width = max(2, int(round(view_state.zoom + tile.river_strength)))

        if tile.river_flow_to and map_data.contains(tile.river_flow_to):
            end_x, end_y = world_to_screen(hex_to_world(tile.river_flow_to, DEFAULT_HEX_RADIUS), view_state)
            pygame.draw.line(
                screen,
                RIVER_COLOR,
                start_point,
                (int(round(end_x)), int(round(end_y))),
                line_width,
            )
        else:
            pygame.draw.circle(screen, RIVER_COLOR, start_point, max(2, line_width))

    draw_hud(screen, map_data, hovered_coord, font)


def draw_hud(screen, map_data: MapData, hovered_coord: HexCoord | None, font) -> None:
    """Draw a compact debug readout across the bottom of the window."""
    import pygame

    width, height = screen.get_size()
    pygame.draw.rect(screen, HUD_BACKGROUND_COLOR, pygame.Rect(0, height - HUD_HEIGHT, width, HUD_HEIGHT))
    label = (
        "Arrows or drag to pan. Mouse wheel or +/- to zoom."
        if hovered_coord is None
        else format_hover_text(map_data.tiles[hovered_coord])
    )
    surface = font.render(label, True, HUD_TEXT_COLOR)
    screen.blit(surface, (10, height - HUD_HEIGHT + 7))


def format_hover_text(tile) -> str:
    """Return a compact hover label for one tile."""
    biome = tile.biome or "water"
    river = "yes" if tile.has_river else "no"
    score = "n/a" if tile.start_suitability is None else f"{tile.start_suitability:.2f}"
    return (
        f"q={tile.coord.q} r={tile.coord.r} biome={biome} elev={tile.elevation:.3f} "
        f"moist={tile.moisture:.3f} temp={tile.temperature:.3f} river={river} start={score}"
    )


def map_pixel_bounds(map_data: MapData, radius: float) -> tuple[float, float, float, float]:
    """Return the world-space bounds of the full pointy-top hex board."""
    min_x = float("inf")
    min_y = float("inf")
    max_x = float("-inf")
    max_y = float("-inf")

    for coord in map_data.tiles:
        center_x, center_y = hex_to_world(coord, radius)
        min_x = min(min_x, center_x - (SQRT_3 / 2.0 * radius))
        max_x = max(max_x, center_x + (SQRT_3 / 2.0 * radius))
        min_y = min(min_y, center_y - radius)
        max_y = max(max_y, center_y + radius)

    return min_x, min_y, max_x, max_y


def hex_to_world(coord: HexCoord, radius: float) -> tuple[float, float]:
    """Convert a pointy-top axial hex coordinate into world-space center pixels."""
    x = radius * SQRT_3 * (coord.q + (coord.r / 2.0))
    y = radius * 1.5 * coord.r
    return x, y


def screen_to_hex_coord(
    map_data: MapData,
    screen_pos: tuple[int, int],
    view_state: ViewState,
) -> HexCoord | None:
    """Map a screen-space position back to a tile coordinate when one exists."""
    world_x = (screen_pos[0] - view_state.offset_x) / view_state.zoom
    world_y = (screen_pos[1] - view_state.offset_y) / view_state.zoom
    guessed_coord = world_to_hex(world_x, world_y, DEFAULT_HEX_RADIUS)
    if map_data.contains(guessed_coord):
        return guessed_coord
    return None


def world_to_hex(x: float, y: float, radius: float) -> HexCoord:
    """Convert world-space center pixels into the nearest pointy-top axial hex."""
    q = ((SQRT_3 / 3.0) * x - (1.0 / 3.0) * y) / radius
    r = ((2.0 / 3.0) * y) / radius
    return axial_round(q, r)


def axial_round(q: float, r: float) -> HexCoord:
    """Round fractional axial coordinates to the nearest hex."""
    x = q
    z = r
    y = -x - z

    rounded_x = round(x)
    rounded_y = round(y)
    rounded_z = round(z)

    x_diff = abs(rounded_x - x)
    y_diff = abs(rounded_y - y)
    z_diff = abs(rounded_z - z)

    if x_diff > y_diff and x_diff > z_diff:
        rounded_x = -rounded_y - rounded_z
    elif y_diff > z_diff:
        rounded_y = -rounded_x - rounded_z
    else:
        rounded_z = -rounded_x - rounded_y

    return HexCoord(q=int(rounded_x), r=int(rounded_z))


def hex_polygon_points(center_x: float, center_y: float, radius: float) -> list[tuple[int, int]]:
    """Return polygon points for a pointy-top hex centered at the given position."""
    points: list[tuple[int, int]] = []
    for index in range(6):
        angle = math.radians(60 * index - 30)
        x = center_x + (radius * math.cos(angle))
        y = center_y + (radius * math.sin(angle))
        points.append((int(round(x)), int(round(y))))
    return points


def world_to_screen(world_pos: tuple[float, float], view_state: ViewState) -> tuple[float, float]:
    """Apply zoom and camera translation to a world-space position."""
    return (
        (world_pos[0] * view_state.zoom) + view_state.offset_x,
        (world_pos[1] * view_state.zoom) + view_state.offset_y,
    )


def zoom_at_screen_position(view_state: ViewState, screen_pos: tuple[int, int], factor: float) -> None:
    """Zoom toward a specific screen-space focus point."""
    target_zoom = clamp(view_state.zoom * factor, MIN_ZOOM, MAX_ZOOM)
    if target_zoom == view_state.zoom:
        return

    world_x = (screen_pos[0] - view_state.offset_x) / view_state.zoom
    world_y = (screen_pos[1] - view_state.offset_y) / view_state.zoom
    view_state.zoom = target_zoom
    view_state.offset_x = screen_pos[0] - (world_x * view_state.zoom)
    view_state.offset_y = screen_pos[1] - (world_y * view_state.zoom)


def polygon_intersects_rect(points: list[tuple[int, int]], rect) -> bool:
    """Return whether a polygon's bounding box intersects a rect."""
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)
    return not (
        max_x < rect.left
        or min_x > rect.right
        or max_y < rect.top
        or min_y > rect.bottom
    )


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a float into an inclusive range."""
    return max(minimum, min(value, maximum))
