# Foundry Local'i kullanabilmek için ilk önce önce SDK'yı indirmek gerekir #
# Foundry Local'ı kullanabilmek için
from foundry_local_sdk import Configuration, FoundryLocalManager
import streamlit as st

#Model yüklenirken ve chat istemcisi oluşturulurken ilerleme durumunu göstermek için callback fonksiyonları tanımlanır.
def ep_progress_callback(ep_name, percent):
    print(f"\r📥 [{ep_name}]: {round(percent)}%", end="\r")

@st.cache_resource
def load_chat_model(model_name="phi-4"):
    config = Configuration(app_name="MyLocalRAGAssistant")
    
    try:
        FoundryLocalManager.initialize(config)
    except Exception:
        pass
        
    # manager yüklenir ve modelin katalogdan alınması için kullanılır.
    manager = FoundryLocalManager.instance
    model = manager.catalog.get_model(model_name)
    manager.download_and_register_eps(progress_callback=ep_progress_callback)
    
    # Model indirilir ve yüklenir.
    model.download()
    model.load()
    
    #Bir chat istemcisi oluşturulur ve kullanıcıdan gelen soruya cevap verilir.
    return model.get_chat_client()

if __name__ == "__main__":
    chat_client = load_chat_model()
    response = chat_client.complete_chat([
        {"role": "user", "content": "Merhaba, nasılsın?"}
    ])
    print(response.choices[0].message.content)