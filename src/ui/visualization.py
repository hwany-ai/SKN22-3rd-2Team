"""
Visualization module for Patent Landscape Map.
Effectively visualizes the relationship between User Idea and Search Results.
"""
import pandas as pd
import plotly.express as px
import streamlit as st

def render_patent_map(result: dict):
    """
    Render an interactive Patent Landscape Map using Plotly.
    
    Visualizes:
    - X-axis: Dense Score (Semantic Similarity)
    - Y-axis: Sparse Score (Keyword Match)
    - Size: Grading Score (Relevance)
    - Color: Risk Level
    """
    search_results = result.get('search_results', [])
    if not search_results:
        st.caption("시각화할 데이터가 충분하지 않습니다.")
        return

    # Prepare data for DataFrame
    data = []
    
    # Add User Idea (The Center/Goal) - Normalized to Max Score approx 1.0 or based on result stats
    # Since dense/sparse scores vary, we plot results relative to each other.
    # We won't plot the user idea as a point because it doesn't have "scores" against itself in this context,
    # or we can assume (1.0, 1.0). Let's stick to patents distribution.
    
    for r in search_results:
        # Normalize scores roughly to 0-100 range for display if they aren't already
        # Dense score usually 0-1 (cosine), Sparse score can be anything (BM25)
        # We use raw scores for relative position
        
        dense = r.get('dense_score', 0)
        sparse = r.get('sparse_score', 0)
        grade = r.get('grading_score', 0) # 0.0 - 1.0
        
        # Determine risk color category based on score
        if grade >= 0.7:
            risk = "High Risk"
        elif grade >= 0.4:
            risk = "Medium Risk"
        else:
            risk = "Low Risk"
            
        data.append({
            "Patent ID": r.get('patent_id'),
            "Title": r.get('title'),
            "Semantic Similarity (Dense)": dense,
            "Keyword Match (Sparse)": sparse,
            "Relevance (Size)": grade * 20 + 5, # Size scaling
            "Risk Level": risk,
            "Abstract": r.get('abstract')[:100] + "..."
        })
        
    df = pd.DataFrame(data)
    
    if df.empty:
        st.write("표시할 데이터가 없습니다.")
        return

    # Create Scatter Plot
    fig = px.scatter(
        df,
        x="Semantic Similarity (Dense)",
        y="Keyword Match (Sparse)",
        size="Relevance (Size)",
        color="Risk Level",
        hover_name="Title",
        hover_data={"Patent ID": True, "Abstract": True, "Relevance (Size)": False},
        color_discrete_map={
            "High Risk": "#dc3545",    # Red
            "Medium Risk": "#ffc107",  # Yellow
            "Low Risk": "#28a745"      # Green
        },
        title="📊 Patent Landscape Map (의미 vs 키워드)",
        template="plotly_dark"  # Looks cool
    )
    
    # Update layout for better aesthetics
    fig.update_layout(
        xaxis_title="🧠 의미적 유사도 (Semantic Concept)",
        yaxis_title="📝 키워드 매칭 (Keyword Match)",
        legend_title="침해 리스크",
        hovermode="closest",
        height=500,
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Pretendard, Malgun Gothic, sans-serif",
            size=14
        )
    )
    
    # Add quadrants or zones if helpful (Optional)
    # fig.add_vline(x=df["Semantic Similarity (Dense)"].mean(), line_width=1, line_dash="dash", line_color="gray")
    # fig.add_hline(y=df["Keyword Match (Sparse)"].mean(), line_width=1, line_dash="dash", line_color="gray")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Explanation
    st.caption("""
    - **우측 상단**: 키워드와 개념 모두 유사한 **가장 위험한 특허**
    - **우측 하단**: 키워드는 다르지만 개념이 유사한 **숨겨진 경쟁자** (주의 필요!)
    - **좌측 상단**: 키워드만 겹치는 **노이즈**일 가능성 높음
    """)
