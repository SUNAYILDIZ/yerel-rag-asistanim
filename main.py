# Foundry Local'i kullanabilmek için ilk önce önce SDK'yı indirmek gerekir #
# Foundry Local'ı kullanabilmek için
from foundry_local_sdk import Configuration, FoundryLocalManager
#Model yüklenirken ve chat istemcisi oluşturulurken ilerleme durumunu göstermek için callback fonksiyonları tanımlanır.
def ep_progress_callback(ep_name, percent):
    print(f"\r📥 [{ep_name}]: {round(percent)}%", end="\r")
config = Configuration(app_name="MyLocalRAGAssistant")
FoundryLocalManager.initialize(config)
# manager yüklenir ve modelin katalogdan alınması için kullanılır.
manager = FoundryLocalManager.instance
model = manager.catalog.get_model("phi-4")
manager.download_and_register_eps(progress_callback=ep_progress_callback)
# Model indirilir ve yüklenir.
model.download()
model.load()
#Bir chat istemcisi oluşturulur ve kullanıcıdan gelen soruya cevap verilir.
chat_client = model.get_chat_client()
response = chat_client.complete_chat([
    {"role": "user", "content": "Merhaba, nasılsın?"}
])
print(response.choices[0].message.content)
