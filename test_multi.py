import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Bar(
    x=[2, 3],
    y=[["Japan", "USA"], ["N-BOX", "CR-V"]],
    orientation='h'
))
fig.update_layout(yaxis=dict(type='multicategory'))
fig.write_image("/Users/fujiikaiya/.gemini/antigravity/scratch/honda-strategy-sim/test.png")
