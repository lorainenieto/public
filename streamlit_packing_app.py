# Smart Packing List - Short Trips (< 4 days) - Streamlit version

from datetime import date
import re
import unicodedata
from copy import deepcopy
import streamlit as st

# -----------------------
# Global constants & data
# -----------------------

MAX_DAYS_AHEAD = 120  # for trip date warning

# Reuse your AIRLINES dictionary as-is
AIRLINES = {
    '1': {'airline': 'Aegean Airlines',
          'dimensions_cm': '56×45×25',
          'extras': None,
          'source_url': 'https://en.aegeanair.com/travel-info/travelling-with-aegean/baggage/baggage-allowance/',
          'weight_kg': '8.0'},

    '2': {'airline': 'Aer Lingus',
          'dimensions_cm': '55×40×24 (48×33×20 on Regional)',
          'extras': '(7 on Regional)',
          'source_url': 'https://www.aerlingus.com/prepare/bags/carry-on-baggage/',
          'weight_kg': '10.0'},

    '3': {'airline': 'Air Europa',
          'dimensions_cm': '55×35×25',
          'extras': None,
          'source_url': 'https://www.aireuropa.com/uk/en/aea/travel-information/baggage/carry-on-luggage.html',
          'weight_kg': '10.0'},

    '4': {'airline': 'Air France',
          'dimensions_cm': '55×35×25',
          'extras': '(Economy total with personal item)',
          'source_url': 'https://russia.airfrance.com/en/information/bagages/bagage-cabine-soute',
          'weight_kg': '12.0'},

    '5': {'airline': 'Austrian Airlines',
          'dimensions_cm': '56×36×23',
          'extras': None,
          'source_url': 'https://www.austrian.com/gb/en/carry-on-baggage',
          'weight_kg': '7.0'},

    '6': {'airline': 'British Airways',
          'dimensions_cm': '56×45×25',
          'extras': 'no limit - (must be able to lift to overhead)',
          'source_url': 'https://www.britishairways.com/content/information/baggage-essentials',
          'weight_kg': None},

    '7': {'airline': 'Brussels Airlines',
          'dimensions_cm': '55×40×23',
          'extras': None,
          'source_url': 'https://www.brusselsairlines.com/us/en/extra-services/baggage/carry-on-baggage',
          'weight_kg': '8.0'},

    '8': {'airline': 'Corendon Airlines',
          'dimensions_cm': '55×40×25',
          'extras': None,
          'source_url': 'https://www.corendonairlines.com/baggage-allowance/hand-luggage',
          'weight_kg': '10.0'},

    '9': {'airline': 'Finnair',
          'dimensions_cm': '55×40×23',
          'extras': '(Economy)',
          'source_url': 'https://www.finnair.com/en/baggage-on-finnair-flights/carry-on-baggage',
          'weight_kg': '8.0'},

    '10': {'airline': 'Iberia',
           'dimensions_cm': '56×40×25',
           'extras': None,
           'source_url': 'https://www.iberia.com/gb/faqs/hand-luggage/',
           'weight_kg': '10.0'},

    '11': {'airline': 'IcelandAir',
           'dimensions_cm': '55×40×20',
           'extras': '(Economy)',
           'source_url': 'https://www.icelandair.com/en-gb/support/baggage/',
           'weight_kg': '10.0'},

    '12': {'airline': 'Jet2',
           'dimensions_cm': '56×45×25',
           'extras': None,
           'source_url': 'https://www.jet2.com/en/faqs?category=hand-luggage-allowances&topic=baggage-and-sports-equipment',
           'weight_kg': '10.0'},

    '13': {'airline': 'KLM',
           'dimensions_cm': '55×35×25',
           'extras': '(Economy total with personal item)',
           'source_url': 'https://www.klm.com/information/baggage/hand-baggage-allowance',
           'weight_kg': '12.0'},

    '14': {'airline': 'Polish Airlines',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://www.lot.com/us/en/help-center/baggage/what-is-the-limit-of-the-carry-on-baggage',
           'weight_kg': '8.0'},

    '15': {'airline': 'Lufthansa',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://www.lufthansa.com/gb/en/carry-on-baggage',
           'weight_kg': '8.0'},

    '16': {'airline': 'Luxair',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://www.luxair.lu/en/information/baggage',
           'weight_kg': '8.0'},

    '17': {'airline': 'Norwegian',
           'dimensions_cm': '55×40×23',
           'extras': '(Flex; combined)',
           'weight_kg': '15.0'},

    '18': {'airline': 'Pegasus Airlines',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'weight_kg': '8.0'},

    '19': {'airline': 'RyanAir',
           'dimensions_cm': '55×40×20',
           'extras': None,
           'source_url': 'https://www.ryanair.com/gb/en/lp/travel-extras/bag-sizers-and-gate-bag-fees-explained',
           'weight_kg': '10.0'},

    '20': {'airline': 'SWISS',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://www.swiss.com/gb/en/prepare/baggage/hand-baggage',
           'weight_kg': '8.0'},

    '21': {'airline': 'Scandinavian Airlines SAS',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://www.sas.se/hjalp-och-kontakt/fragor-och-svar/baggage/hur-mycket-kabinbagage-kan-jag-ta-med-mig/',
           'weight_kg': '8.0'},

    '22': {'airline': 'SunExpress',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://www.sunexpress.com/en-gb/information/luggage-info/hand-baggage/',
           'weight_kg': '8.0'},

    '23': {'airline': 'Air Portugal TAP',
           'dimensions_cm': '55×40×20',
           'extras': '(Europe; some routes 10)',
           'source_url': 'https://www.flytap.com/en-gb/information/baggage/hand-baggage',
           'weight_kg': '8.0'},

    '24': {'airline': 'TUI Airways',
           'dimensions_cm': '55×40×20',
           'extras': None,
           'source_url': 'https://www.tui.co.uk/destinations/info/luggage-allowance',
           'weight_kg': '10.0'},

    '25': {'airline': 'Transavia',
           'dimensions_cm': '55×40×25',
           'extras': '(combined hand + cabin bag)',
           'source_url': 'https://www.transavia.com/help/en-eu/baggage/cabin-baggage/how-much-to-bring',
           'weight_kg': '10.0'},

    '26': {'airline': 'Transavia France',
           'dimensions_cm': '55×40×25',
           'extras': '(combined hand + cabin bag)',
           'source_url': 'https://www.transavia.com/help/en-eu/baggage/cabin-baggage',
           'weight_kg': '10.0'},

    '27': {'airline': 'Turkish Airlines',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://www.turkishairlines.com/en-int/any-questions/carry-on-baggage/',
           'weight_kg': '8.0'},

    '28': {'airline': 'Virgin Atlantic',
           'dimensions_cm': '56×36×23',
           'extras': '(Economy/Premium)',
           'source_url': 'https://www.virginatlantic.com/en-EU/help/categories/d8087189-4ce8-4491-8b61-f62b3b677a15',
           'weight_kg': '10.0'},

    '29': {'airline': 'Vueling',
           'dimensions_cm': '55×40×20',
           'extras': None,
           'source_url': 'https://help.vueling.com/hc/en-gb/articles/19798835176081-Hand-Luggage-Allowance-Cabin-bags-allowance',
           'weight_kg': '10.0'},

    '30': {'airline': 'vueling (for Spain)',
           'dimensions_cm': '55×40×20',
           'extras': None,
           'source_url': 'https://help.vueling.com/hc/en-gb/articles/19798835176081-Hand-Luggage-Allowance-Cabin-bags-allowance',
           'weight_kg': '10.0'},

    '31': {'airline': 'Wizz Air',
           'dimensions_cm': '55×40×23',
           'extras': None,
           'source_url': 'https://wizzair.com/information-and-services/travel-information/baggage',
           'weight_kg': '10.0'},

    '32': {'airline': 'AirBaltic',
           'dimensions_cm': '55×40×23',
           'extras': ' (standard; options to buy more)',
           'source_url': 'https://www.airbaltic.com/en/baggage/',
           'weight_kg': '8.0'},

    '33': {'airline': 'EasyJet',
           'dimensions_cm': '56×45×25',
           'extras': None,
           'source_url': 'https://www.easyjet.com/en/help-centre/policy-terms-and-conditions/fees-charges',
           'weight_kg': '15.0'}
}

def _strip_accents(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))

def _normalize_name(s: str) -> str:
    s = _strip_accents(s.lower())
    s = re.sub(r'\(.*?\)', ' ', s)                 # remove parenthetical notes
    s = re.sub(r'\b(airlines?|airways)\b', ' ', s) # drop generic words
    s = re.sub(r'[^a-z0-9]+', ' ', s)              # keep alnum
    return re.sub(r'\s+', ' ', s).strip()

def build_airline_index(airlines: dict) -> dict:
    idx = {}
    for rec in airlines.values():
        name = rec.get("airline", "")
        if not name:
            continue
        n = _normalize_name(name)
        if n:
            idx[n] = rec
            idx[n.replace(" ", "")] = rec

    aliases = {
        "ba": "British Airways",
        "klm": "KLM",
        "sas": "Scandinavian Airlines SAS",
        "lot": "Polish Airlines",
        "tap": "Air Portugal TAP",
        "virgin": "Virgin Atlantic",
        "wizz": "Wizz Air",
        "vueling spain": "vueling (for Spain)",
        "ryanair": "RyanAir",
    }
    name_to_rec = {v["airline"]: v for v in airlines.values()}
    for alias, canonical in aliases.items():
        rec = name_to_rec.get(canonical)
        if rec:
            a = _normalize_name(alias)
            idx[a] = rec
            idx[a.replace(" ", "")] = rec
    return idx

_dim_re = re.compile(r'^\s*(\d{2,3})\s*[x×]\s*(\d{2,3})\s*[x×]\s*(\d{2,3})\s*$')

def parse_dimensions(raw: str):
    raw = raw.lower().replace(" ", "")
    raw = raw.replace("x", "×")
    match = _dim_re.match(raw.replace('×', 'x'))
    if not match:
        return None
    L, W, H = match.groups()
    return f"{L}×{W}×{H}"

# -----------------------
# Activities & items
# -----------------------

activity_template = {
    "Sightseeing": {
        "Daypack": 1,
        "City Walking Shoes": 1,
        "Camera": 1
    },
    "Family / Friends": {
        "Gift / Small Present": 1
    },
    "Swimming / Surfing": {
        "Swimwear": 1,
        "Swim Goggles": 1,
        "Beach Towel": 1,
        "Rash Guard / Wetsuit": 1
    },
    "Outdoor / Adventure": {
        "Hiking Boots": 1,
        "Rain Jacket": 1,
        "Day Hiking Pack": 1
    },
    "Work / Study": {
        "Notebook / Laptop": 1,
        "Notebook / Study Materials": 1
    },
    "Formal Event / Party": {
        "Shirt / Blouse (Formal)": 1,
        "Dress / Suit": 1,
        "Formal Shoes": 1
    }
}

activity_weight = {
    "Daypack":               {"weather": "All", "weight": 0.50},
    "City Walking Shoes":    {"weather": "All", "weight": 0.80},
    "Camera":                {"weather": "All", "weight": 0.40},
    "Gift / Small Present":  {"weather": "All", "weight": 0.30},
    "Swim Goggles":          {"weather": "All", "weight": 0.10},
    "Beach Towel":           {"weather": "All", "weight": 0.40},
    "Rash Guard / Wetsuit":  {"weather": "All", "weight": 0.70},
    "Hiking Boots":          {"weather": "All", "weight": 1.20},
    "Rain Jacket":           {"weather": "All", "weight": 0.40},
    "Day Hiking Pack":       {"weather": "All", "weight": 0.60},
    "Notebook / Laptop":     {"weather": "All", "weight": 1.50},
    "Notebook / Study Materials": {"weather": "All", "weight": 0.80},
    "Shirt / Blouse (Formal)": {"weather": "All", "weight": 0.20},
    "Dress / Suit":          {"weather": "All", "weight": 0.80},
    "Formal Shoes":          {"weather": "All", "weight": 1.00},
}

# Clothes and templates (same as your code)
clothes = {
    # Freezing
    "Heavy Coat":      {"weather": "Freezing", "weight": 1.0},
    "Thermal Shirt":   {"weather": "Freezing", "weight": 0.25},
    "Thermal Leggings":{"weather": "Freezing", "weight": 0.30},
    "Wool Sweater":    {"weather": "Freezing", "weight": 0.50},
    "Long-Sleeve Shirt":{"weather": "Freezing", "weight": 0.20},
    "Jeans":           {"weather": "Freezing", "weight": 0.60},
    "Winter Pants":    {"weather": "Freezing", "weight": 0.70},
    "Scarf":           {"weather": "Freezing", "weight": 0.20},
    "Beanie":          {"weather": "Freezing", "weight": 0.10},
    "Gloves":          {"weather": "Freezing", "weight": 0.15},
    "Thick Socks":     {"weather": "Freezing", "weight": 0.10},
    "Undershirt":      {"weather": "Freezing", "weight": 0.15},
    "Boots":           {"weather": "Freezing", "weight": 1.20},

    # Cold
    "Coat":            {"weather": "Cold", "weight": 0.80},
    "Sweater":         {"weather": "Cold", "weight": 0.45},
    "Cardigan":        {"weather": "Cold", "weight": 0.40},
    "Long-Sleeve Shirt (Cold)": {"weather": "Cold", "weight": 0.20},
    "Turtleneck":      {"weather": "Cold", "weight": 0.30},
    "Jeans (Cold)":    {"weather": "Cold", "weight": 0.60},
    "Warm Pants":      {"weather": "Cold", "weight": 0.70},
    "Warm Socks":      {"weather": "Cold", "weight": 0.10},
    "Closed Shoes":    {"weather": "Cold", "weight": 0.90},
    "Scarf (Cold)":    {"weather": "Cold", "weight": 0.20},
    "Beanie (Cold)":   {"weather": "Cold", "weight": 0.10},

    # Cool
    "Light Jacket":    {"weather": "Cool", "weight": 0.40},
    "Sweatshirt":      {"weather": "Cool", "weight": 0.35},
    "Hoodie":          {"weather": "Cool", "weight": 0.45},
    "T-shirt":         {"weather": "Cool", "weight": 0.15},
    "Long-Sleeve Shirt (Cool)": {"weather": "Cool", "weight": 0.20},
    "Jeans (Cool)":    {"weather": "Cool", "weight": 0.60},
    "Chinos":          {"weather": "Cool", "weight": 0.50},
    "Sneakers":        {"weather": "Cool", "weight": 0.70},
    "Socks":           {"weather": "Cool", "weight": 0.05},

    # Warm
    "Short-Sleeve Top": {"weather": "Warm", "weight": 0.12},
    "T-shirt (Warm)":   {"weather": "Warm", "weight": 0.15},
    "Light Pants":      {"weather": "Warm", "weight": 0.35},
    "Shorts":           {"weather": "Warm", "weight": 0.20},
    "Casual Dress":     {"weather": "Warm", "weight": 0.25},
    "Sneakers (Warm)":  {"weather": "Warm", "weight": 0.70},
    "Socks (Warm)":     {"weather": "Warm", "weight": 0.05},
    "Light Jacket (Evening)": {"weather": "Warm", "weight": 0.35},
    "Sun Hat (Warm)":   {"weather": "Warm", "weight": 0.10},

    # Hot
    "Tank Top":         {"weather": "Hot", "weight": 0.10},
    "T-shirt (Hot)":    {"weather": "Hot", "weight": 0.15},
    "Shorts (Hot)":     {"weather": "Hot", "weight": 0.20},
    "Summer Dress":     {"weather": "Hot", "weight": 0.25},
    "Light Shirt":      {"weather": "Hot", "weight": 0.18},
    "Swimwear":         {"weather": "Hot", "weight": 0.15},
    "Flip-Flops":       {"weather": "Hot", "weight": 0.20},
    "Sun Hat":          {"weather": "Hot", "weight": 0.10},
    "Light Sandals":    {"weather": "Hot", "weight": 0.30},
    "Beach Cover-Up":   {"weather": "Hot", "weight": 0.20},

    # All
    "Toiletries": {"weather": "All", "weight": 0.80},
}

template = {
    "Freezing": {
        "Heavy Coat": 1, "Thermal Shirt": 2, "Thermal Leggings": 2,
        "Wool Sweater": 1, "Long-Sleeve Shirt": 2, "Jeans": 1,
        "Winter Pants": 1, "Scarf": 1, "Beanie": 1, "Gloves": 1,
        "Thick Socks": 3, "Undershirt": 2, "Boots": 1, "Toiletries": 1},

    "Cold": {
        "Coat": 1, "Sweater": 1, "Cardigan": 1,
        "Long-Sleeve Shirt (Cold)": 2, "Turtleneck": 1,
        "Jeans (Cold)": 1, "Warm Pants": 1, "Warm Socks": 3,
        "Closed Shoes": 1, "Scarf (Cold)": 1, "Beanie (Cold)": 1,
        "Toiletries": 1},

    "Cool": {
        "Light Jacket": 1, "Sweatshirt": 1, "Hoodie": 1,
        "T-shirt": 2, "Long-Sleeve Shirt (Cool)": 1,
        "Jeans (Cool)": 1, "Chinos": 1, "Sneakers": 1,
        "Socks": 3, "Toiletries": 1},

    "Warm": {
        "Short-Sleeve Top": 2, "T-shirt (Warm)": 2,
        "Light Pants": 1, "Shorts": 1, "Casual Dress": 1,
        "Sneakers (Warm)": 1, "Socks (Warm)": 3,
        "Light Jacket (Evening)": 1, "Sun Hat (Warm)": 1,
        "Toiletries": 1},

    "Hot": {
        "Tank Top": 2, "T-shirt (Hot)": 2, "Shorts (Hot)": 2,
        "Summer Dress": 1, "Light Shirt": 1, "Swimwear": 1,
        "Flip-Flops": 1, "Sun Hat": 1, "Light Sandals": 1,
        "Beach Cover-Up": 1, "Toiletries": 1}
}

# -----------------------
# Weight / trimming logic
# -----------------------

WEIGHT_TABLE = {}
WEIGHT_TABLE.update(clothes)
WEIGHT_TABLE.update(activity_weight)

PRIORITY_RANK = {"Underwear": 0, "Socks": 1, "T-shirt": 2, "Jeans": 2,
                 "Sneakers": 4, "Toiletries": 5}

HARD_KEEP = {"Underwear", "Socks"}

def _priority(item):
    return PRIORITY_RANK.get(item, 5)

def total_weight(quantities, weight_table):
    w = 0.0
    for item, qty in quantities.items():
        if item in weight_table:
            w += weight_table[item]["weight"] * qty
    return round(w, 3)

def greedy_trim_to_limit_verbose(items, weight_table, limit_kg,
                                 safety_buffer=0.3, respect_hard_keep=True, max_passes=2):
    target = max(0.0, float(limit_kg) - float(safety_buffer))
    current = deepcopy(items)
    before = total_weight(current, weight_table)
    removed_trace = []
    if before <= target:
        info = {"before": before, "after": before, "removed": [], "note": "Already within target."}
        return current, info

    def sorted_units(avoid_hard):
        units = [(i, 1) for i, q in current.items() for _ in range(q)]
        def key(u):
            item = u[0]
            pri = _priority(item)
            if avoid_hard and item in HARD_KEEP:
                pri = -100
            w = weight_table.get(item, {}).get("weight", 0.0)
            return (pri, w)
        units.sort(key=key, reverse=True)
        return units

    for pass_id in range(max_passes):
        avoid_hard = respect_hard_keep and pass_id == 0
        units = sorted_units(avoid_hard)
        for item, _ in units:
            if total_weight(current, weight_table) <= target:
                break
            if avoid_hard and item in HARD_KEEP:
                continue
            if current.get(item, 0) > 0:
                current[item] -= 1
                if current[item] == 0:
                    del current[item]
                removed_trace.append(item)
        if total_weight(current, weight_table) <= target:
            break

    after = total_weight(current, weight_table)
    note = "Reached target." if after <= target else "Could not reach target without cutting essentials."
    info = {"before": before, "after": after, "removed": removed_trace, "note": note}
    return current, info

# -----------------------
# Streamlit UI helpers
# -----------------------

def get_airline_info(airline_name: str):
    index = build_airline_index(AIRLINES)
    key1 = _normalize_name(airline_name)
    key2 = key1.replace(" ", "")
    rec = index.get(key1) or index.get(key2)
    return rec

def build_initial_items(weather_key: str, activities_selected):
    items = template[weather_key].copy()
    for act in activities_selected:
        extra_items = activity_template.get(act, {})
        for item, qty in extra_items.items():
            items[item] = items.get(item, 0) + qty
    return items

def show_items_editor():
    """Render number_inputs for each item in session_state['items']."""
    items = st.session_state["items"]
    new_items = {}
    for item, qty in items.items():
        new_qty = st.number_input(
            item,
            min_value=0,
            value=int(qty),
            step=1,
            key=f"qty_{item}"
        )
        if new_qty > 0:
            new_items[item] = int(new_qty)
    st.session_state["items"] = new_items

def show_weight_box(limit_kg_str):
    items = st.session_state.get("items", {})
    total = total_weight(items, WEIGHT_TABLE)
    if limit_kg_str and limit_kg_str != "0":
        try:
            limit = float(limit_kg_str)
        except ValueError:
            limit = None
    else:
        limit = None

    if limit is None:
        st.info(f"Estimated total weight: **{total:.2f} kg**")
        return

    target = limit - 0.3
    margin = round(target - total, 2)
    if margin >= 0.8:
        st.success(f"Total weight: **{total:.2f} kg**  | Limit: {limit} kg → ✅ OK")
    elif margin >= 0:
        st.warning(f"Total weight: **{total:.2f} kg**  | Limit: {limit} kg → ⚠️ Close to limit")
    else:
        st.error(f"Total weight: **{total:.2f} kg**  | Limit: {limit} kg → ❌ Over the limit")

def main():
    st.title("Smart Packing List - Short Trips (< 4 days) ✈️")
    st.write("Let’s get you ready for your next trip.")

    if "items" not in st.session_state:
        st.session_state["items"] = {}
    if "removed_items" not in st.session_state:
        st.session_state["removed_items"] = []

    # 1. Basic info + trip details
    with st.form("trip_form"):
        st.subheader("1. Traveller & Trip Details")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("What’s your name?")
            gender = st.selectbox(
                "How would you define your gender?",
                ["Male", "Female", "Non-Binary", "Other", "Wish not to answer"]
            )
        with col2:
            destination = st.text_input("Where are you traveling to?")
            today = date.today()
            trip_start = st.date_input(
                "When does your trip start?",
                min_value=today,
                help="Weather advice is better if your trip is within the next 2 weeks."
            )

        col3, col4 = st.columns(2)
        with col3:
            nights = st.number_input("How many nights/evenings will you be away?",
                                     min_value=0, max_value=4, step=1)
        with col4:
            full_days = st.number_input("How many full days will you have there?",
                                        min_value=0, max_value=3, step=1,
                                        help="This tool is for trips under 4 days.")

        st.markdown("---")
        st.subheader("2. Airline & Cabin Baggage")

        airline_name = st.text_input("Which airline are you travelling with?")
        use_manual_rules = st.checkbox("My airline isn’t listed / I want to enter baggage rules manually")

        airline_rec = None
        weight_kg_str = None
        dims_str = None

        if airline_name and not use_manual_rules:
            airline_rec = get_airline_info(airline_name)
            if airline_rec:
                st.info(
                    f"**{airline_rec['airline']}**\n\n"
                    f"- Max weight: "
                    f"{'no fixed published limit (must be able to lift to overhead)' if airline_rec['weight_kg'] is None else str(airline_rec['weight_kg']) + ' kg'}  "
                    f"{('(' + airline_rec['extras'] + ')') if airline_rec.get('extras') else ''}\n"
                    f"- Max dimensions: {airline_rec.get('dimensions_cm', 'n/a')}\n"
                    f"- Source: {airline_rec.get('source_url', 'n/a')}"
                )
                weight_kg_str = "0" if airline_rec["weight_kg"] is None else str(airline_rec["weight_kg"])
                dims_str = airline_rec.get("dimensions_cm")
            else:
                st.warning("I couldn’t find that airline in the built-in list. You can enter custom rules below.")
                use_manual_rules = True

        if use_manual_rules:
            weight_val = st.number_input(
                "Max carry-on weight in kg (0 if no fixed limit):",
                min_value=0.0, value=10.0, step=0.5
            )
            weight_kg_str = "0" if weight_val == 0 else str(weight_val)
            raw_dims = st.text_input("Max dimensions in cm (e.g., 55x40x23)")
            dims_parsed = parse_dimensions(raw_dims) if raw_dims else None
            if raw_dims and not dims_parsed:
                st.error("Please use a pattern like 55x40x23 (only numbers).")
            dims_str = dims_parsed or raw_dims or None

        st.markdown("---")
        st.subheader("3. Activities & Weather")

        activities_list = [
            "Sightseeing",
            "Family / Friends",
            "Swimming / Surfing",
            "Outdoor / Adventure",
            "Work / Study",
            "Formal Event / Party"
        ]

        activities_selected = st.multiselect(
            "What activities will you do on this trip?",
            activities_list
        )

        temp_choice = st.radio(
            "What is the average expected temperature?",
            [
                "Freezing (<0°C)",
                "Cold (0°C - 10°C)",
                "Cool (11°C - 20°C)",
                "Warm (20°C - 25°C)",
                "Hot (>25°C)",
            ]
        )

        submitted = st.form_submit_button("Generate packing list")

    #  Small informational warnings about date
    if submitted:
        days_until = (trip_start - today).days
        if days_until > MAX_DAYS_AHEAD:
            st.warning(f"That date is in {days_until} days — packing advice might not be very accurate.")
        elif days_until > 14:
            st.info(
                f"Your trip is in {days_until} days. "
                "Weather forecasts beyond ~1 week can be uncertain, so treat this list as a rough guide."
            )

        # Validate trip length
        if nights > 4 or full_days >= 4:
            st.error("This app is only meant for short trips (< 4 days). Reduce nights/days to continue.")
            return

        if not name or not destination:
            st.error("Please fill in at least your name and destination.")
            return

        # Map temp_choice to your template key
        weather_map = {
            "Freezing (<0°C)": "Freezing",
            "Cold (0°C - 10°C)": "Cold",
            "Cool (11°C - 20°C)": "Cool",
            "Warm (20°C - 25°C)": "Warm",
            "Hot (>25°C)": "Hot",
        }
        weather_key = weather_map[temp_choice]

        # Build initial items and store in session
        items = build_initial_items(weather_key, activities_selected)
        st.session_state["items"] = items
        st.session_state["removed_items"] = []

        st.success(
            f"Packing list created for **{name.strip().title()}** "
            f"travelling to **{destination.strip().title()}** ✈️"
        )

    # 4. Show & edit packing list if it exists
    if st.session_state["items"]:
        st.markdown("## 4. Your packing list")
        show_items_editor()
        show_weight_box(weight_kg_str)

        # Auto-trim section
        if weight_kg_str and weight_kg_str != "0":
            if st.button("Auto-trim to fit airline weight limit"):
                try:
                    limit_val = float(weight_kg_str)
                    trimmed, info = greedy_trim_to_limit_verbose(
                        st.session_state["items"],
                        WEIGHT_TABLE,
                        limit_val,
                        safety_buffer=0.3,
                        respect_hard_keep=True,
                        max_passes=2
                    )
                    st.session_state["items"] = trimmed
                    st.session_state["removed_items"] = info.get("removed", [])
                    st.success(
                        f"Trimmed from {info['before']:.2f} kg to {info['after']:.2f} kg. {info.get('note', '')}"
                    )
                except ValueError:
                    st.error("Could not parse airline weight limit; trimming skipped.")

        if st.session_state["removed_items"]:
            st.info("Items removed during auto-trim: " + ", ".join(st.session_state["removed_items"]))

        # Show final summary
        st.markdown("---")
        st.subheader("Final Summary")
        final_weight = total_weight(st.session_state["items"], WEIGHT_TABLE)
        st.write(f"**Total estimated weight:** {final_weight:.2f} kg")
        st.write("You’re ready to pack! ✅")

if __name__ == "__main__":
    main()
