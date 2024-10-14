import streamlit as st
from tensorflow.keras.models import load_model  # type: ignore
from PIL import Image
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
from io import BytesIO
#dùng chức năng của file download image
from views.download_image import download_image, cleanup_temp_file

# Load the saved model
@st.cache_resource
def load_model_cached():
    return load_model('vgg19_model.h5')

model = load_model_cached()

# Include external CSS and JavaScript files
st.markdown('<link rel="stylesheet" href="static/styles.css">', unsafe_allow_html=True)
st.markdown('<script src="static/script.js"></script>', unsafe_allow_html=True)

st.title('🍎 Fruit Classifier')

if 'fruit_df' not in st.session_state:
    st.session_state.fruit_df = pd.DataFrame(columns=['Fruit', 'Count'])

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Upload or Drag & Drop an image")
    
    upload_option = st.radio("Choose upload method:", ("File Upload", "Image URL"))
    
    image_file = None
    if upload_option == "File Upload":
        uploaded_file = st.file_uploader("Choose an image or drag and drop here", type=["jpg", "jpeg", "png", "webp"], key="file_uploader")
        if uploaded_file is not None:
            image_file = Image.open(uploaded_file)
    elif upload_option == "Image URL":
        url = st.text_input("Enter the URL of the image:")
        if url:
            temp_file = download_image(url)
            if temp_file:
                image_file = Image.open(temp_file)
            else:
                st.error("Failed to download the image. Please check the URL and try again.")
                st.stop()


    ##Old code
    # uploaded_file = st.file_uploader("Choose an image or drag and drop here", type=["jpg", "jpeg", "png", "webp"], key="file_uploader")
    
    # if uploaded_file is not None:
    #     image = Image.open(uploaded_file)
    # elif 'url' in st.query_params:
    #     url = st.query_params['url']
    #     response = requests.get(url)
    #     image = Image.open(BytesIO(response.content))
    # else:
    #     st.stop()

    # if image_file is not None:
    #     st.image(image_file, caption='Uploaded Image', use_column_width=True)


    # # Image processing
    # img = image_file.resize((224, 224))
    # img = np.array(img) / 255.0
    # img = np.expand_dims(img, axis=0)

    # Prediction
    if image_file is not None:
        st.image(image_file, caption='Uploaded Image', use_column_width=True)

        # Image processing
        img = image_file.resize((224, 224))
        img = np.array(img) / 255.0
        img = np.expand_dims(img, axis=0)
        
        # Prediction
        with st.spinner('Analyzing the image...'):
            prediction = model.predict(img)

        fruit_classes = ['Apple', 'Banana', 'Grapes', 'Kiwi', 'Mango', 'Orange', 'Strawberry']
        predicted_class_index = np.argmax(prediction[0])
        predicted_class = fruit_classes[predicted_class_index]
        confidence = prediction[0][predicted_class_index] * 100

        # Update session state
        if predicted_class in st.session_state.fruit_df['Fruit'].values:
            st.session_state.fruit_df.loc[st.session_state.fruit_df['Fruit'] == predicted_class, 'Count'] += 1
        else:
            new_row = pd.DataFrame({'Fruit': [predicted_class], 'Count': [1]})
            st.session_state.fruit_df = pd.concat([st.session_state.fruit_df, new_row], ignore_index=True)

        # Display prediction results
        with col2:
            st.markdown("### 🧠 AI Prediction")
            st.markdown(f"""
            <div class='prediction-box'>
                <h2 style='color: #4CAF50; margin-bottom: 10px;'>{predicted_class}</h2>
                <p>Confidence: <span style='color: #4CAF50; font-weight: bold;'>{confidence:.2f}%</span></p>
            </div>
            """, unsafe_allow_html=True)

            # Fruit information
            fruit_info = {
                'Apple': "Apples are rich in fiber, vitamins, and antioxidants. They may help reduce the risk of heart disease and diabetes.",
                'Banana': "Bananas are high in potassium and fiber. They support heart health and aid digestion.",
                'Grapes': "Grapes are packed with antioxidants like resveratrol. They may have anti-aging properties and support heart health.",
                'Kiwi': "Kiwis are high in vitamin C and fiber. They support immune function and digestive health.",
                'Mango': "Mangoes are rich in vitamins A and C. They support eye health and boost the immune system.",
                'Orange': "Oranges are known for their high vitamin C content. They support immune function and skin health.",
                'Strawberry': "Strawberries are low in calories but high in vitamin C and antioxidants. They may help improve heart health and blood sugar control."
            }

            st.markdown(f"""
            <div class='fruit-info-box'>
                <h4 style='color: #4CAF50; margin-bottom: 10px;'>🍏 More about {predicted_class}:</h4>
                <p>{fruit_info[predicted_class]}</p>
            </div>
            """, unsafe_allow_html=True)

            # Fun fact
            fruit_facts = {
                'Apple': "There are over 7,500 varieties of apples grown worldwide, each with its unique flavor profile!",
                'Banana': "Bananas are berries, but strawberries aren't! Botanically, bananas are classified as berries.",
                'Grapes': "It takes about 2.5 pounds of grapes to produce one bottle of wine.",
                'Kiwi': "Kiwifruit is also known as Chinese gooseberry and was renamed for marketing purposes.",
                'Mango': "Mangoes belong to the same family as cashews and pistachios!",
                'Orange': "Orange trees can live and produce fruit for up to 100 years under optimal conditions.",
                'Strawberry': "Strawberries are the only fruit with seeds on the outside, with the average berry having about 200 seeds!"
            }

            st.markdown(f"""
            <div class='fun-fact-box'>
                <h4 style='color: #4CAF50; margin-bottom: 10px;'>🎉 Fun Fruit Fact:</h4>
                <p>{fruit_facts[predicted_class]}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Please upload an image to start the prediction.")



if image_file is not None:
    st.markdown("### 📊 Fruit Prediction Statistics")

    fruit_emojis = {
        'Apple': '🍎',
        'Banana': '🍌',
        'Grapes': '🍇',
        'Kiwi': '🥝',
        'Mango': '🥭',
        'Orange': '🍊',
        'Strawberry': '🍓'
    }

    fig = go.Figure()

    for index, row in st.session_state.fruit_df.iterrows():
        fruit = row['Fruit']
        count = row['Count']
        emoji = fruit_emojis.get(fruit, '')

        fig.add_trace(go.Bar(
            x=[fruit],
            y=[count],
            name=fruit,
            text=[f"{fruit} {emoji}"],  
            textposition='outside',
            hoverinfo='text',
            hovertext=f"{fruit}: {count}",
            marker_color=['#4CAF50', '#FFC107', '#FF5733', '#3498DB', '#8E44AD', '#E67E22', '#16A085', '#F39C12'][index % 8]
        ))

    fig.update_layout(
        title={
            'text': 'Fruit Prediction Count',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Fruit Type",
        yaxis_title="Number of Predictions",
        showlegend=False,
        xaxis={'categoryorder': 'total descending'}
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class='footer'>
        <p>Thank you for coming ❤️</p>
    </div>
    """, unsafe_allow_html=True)

    # Clean up temp file
    if 'temp_file' in locals():
        cleanup_temp_file(temp_file)
