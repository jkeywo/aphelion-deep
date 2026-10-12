"""Game-owned replay language; presentation only, never applies effects."""

PLAYER_NAMES = {
    "engineer": "Fabrication Lead",
    "lead": "Lead Ecologist",
    "systems": "Systems Ecologist",
}


def describe(event_type, keys, data, engine):
    def card(key):
        return engine.defs.get(key, {}).get("Name", key)

    def player(key):
        return PLAYER_NAMES.get(key, key)

    def resources(values):
        return ", ".join(f"{amount} {name}" for name, amount in values.items()) or "no resources"

    subject = card(keys[0]) if keys else ""
    location = engine.loc(keys[0][0])["name"] if keys else ""
    actor = player(data.get("actor", ""))
    if event_type == "simulation.started":
        return "Prepare the three-player tutorial. The ordered decks are ready; no locations have been explored."
    if event_type == "turn.started":
        moves = "; ".join(f"{player(p)} goes to {engine.loc(l)['name']}" for p, l in data["assignments"].items())
        return f"Begin turn {engine.turn}: {moves}."
    if event_type == "players.assigned":
        moves = "; ".join(f"{player(p)} goes to {engine.loc(l)['name']}" for p, l in data["assignments"].items())
        return f"Confirm all {data['phase'].lower()} assignments together: {moves}."
    if event_type == "card.drawn":
        return f"Draw {subject} at {location}. Read its back before flipping it."
    if event_type == "card.activated":
        return f"{actor} spends 2 Materials at {location}, flips {subject}, and sets Scanning to 4."
    if event_type == "card.flipped":
        return f"Flip {subject} at {location} to its front."
    if event_type == "card.gained":
        return f"{player(data['recipient'])} takes {subject} into their hand."
    if event_type == "exploration.gate":
        comparisons = ", ".join(f"{data['available'].get(k, 0)} of {v} required {k}" for k, v in data["requirements"].items())
        outcome = "The gate opens; exploration can continue" if data["open"] else "The gate stays closed; exploration stops here"
        return f"Attempt {subject} at {location}: {comparisons}. {outcome}."
    if event_type == "card.revealed" and engine.defs[keys[0]]["Card Type"] == "Phase Reference":
        return f"Place {subject} in play at {location}. It automatically shows the current phase."
    if event_type == "card.revealed":
        return f"Reveal {subject} at {location} (card {data['deck_position']} in its ordered deck)."
    if event_type == "player.cultivated":
        return f"{actor} uses Cultivator on {subject} at {location}, adding 1 Population up to the track limit."
    if event_type == "dilemma.resolved":
        outcomes = {
            "Restart": "Gain 2 local Power and advance the reactor by 1.",
            "Protect": "Filterweed and Spotted Grazers each gain 2 Population, up to their track limits.",
            "Cut it free": "Giant Lungweed gains 2 Population, up to its track limit, and the location gains 1 Materials.",
        }
        return f"Choose ‘{data['choice']}’ for {subject} at {location}. {outcomes[data['choice']]} Remove the dilemma."
    if event_type == "player.ate":
        payment = data["payment"]
        food = "the available Food icon" if payment == "Food icon" else f"1 {'Rations' if payment == keys[0] else 'Population'} from {card(payment)}"
        return f"{actor} eats at {location}, using {food}."
    if event_type == "ecosystem.starved":
        return f"{subject} cannot pay its full feeding cost of {data['required']} at {location}. It consumes nothing and suffers starvation."
    if event_type == "ecosystem.fed":
        targets = ", ".join(card(k) for k in keys[1:])
        return f"{subject} feeds at {location}, consuming {data['amount']} Population from the selected targets in order: {targets}."
    if event_type == "card.upkeep":
        key = keys[0]
        if key in ("R12", "C12"):
            choice = engine.script["choices"][f"{engine.turn}:convert:{key}"]
            if choice == "grow":
                return f"Let {subject} grow at {location}, adding 1 Abundance up to the track limit."
            produced = {k: v * (2 if key == "C12" else 1) for k, v in choice.items()}
            return f"Convert {sum(choice.values())} Abundance from {subject} at {location} into {resources(produced)}."
        return f"Complete mandatory upkeep for {subject} at {location}."
    if event_type == "player.crafted":
        return f"{actor} crafts {subject} at {location}, paying {resources(data['cost'])} after any Fabricator discount."
    if event_type == "policy.optional_actions":
        choices = "; ".join(f"{card(k.split(':')[0])}{' harvest' if ':' in k else ''}: {v}" for k, v in data["decisions"].items())
        return f"Record optional action choices: {choices or 'none available'}."
    if event_type == "card.no_longer_in_play":
        return f"{subject} is no longer in play at {location}; an earlier mandatory effect removed it."
    if event_type == "event.bloom":
        return f"Resolve {subject} at {location}: each Kelp Flora gains 1 Population, up to its track limit. Discard the event."
    if event_type == "turn.completed":
        return f"Finish turn {engine.turn}. All revealed locations have resolved upkeep and the declared optional choices are recorded."
    if event_type == "simulation.completed":
        return "The three-turn tutorial is complete. Inspect the final players, locations and reactor state below."
    if event_type == "simulation.blocked":
        return "The tutorial is blocked: " + "; ".join(data["blockers"])
    raise ValueError("Missing replay description: " + event_type)
