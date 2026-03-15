import pandas as pd
from engine.simulator import SimulationEngine
from data.sample_data import generate_sample_data
from layouts.timeline import create_timeline_chart

df = generate_sample_data()
engine = SimulationEngine(df)
timeline = engine.get_timeline_data()

try:
    fig = create_timeline_chart(timeline)
    print("Success!")
except Exception as e:
    import traceback
    traceback.print_exc()
