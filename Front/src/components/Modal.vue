<template>
  <div class="modal-backdrop" @click.self="$emit('close')">

    <ModalImage
        :visible="showImageModal"
        :imageSrc="imageSrc"
        @close="showImageModal = false"
    />

    <div class="modal">
      <h3>Действия с фрагментом</h3>
      <p><strong>Entity ID:</strong> {{ feature?.properties.entityid }}</p>
      <p><strong>Product ID:</strong> {{ feature?.properties.productid }}</p>

      <div class="actions">
        <div class="action-row">
          <button class="action-button" @click="combineBands">Объединить каналы изображений (7)</button>
          <button class="eye-button" @click="() => viewFragment('combine')">
            <EyeIcon />
          </button>
        </div>

        <div class="action-row">
          <button class="action-button" @click="generateMask">Сформировать маску</button>
          <button class="eye-button" @click="() => viewFragmentMask('mask')">
            <EyeIcon />
          </button>
        </div>

        <div class="action-row">
          <button class="action-button" @click="detectFire">Обнаружить пожар</button>
          <button class="eye-button" @click="() => viewFragmentMask('fire')">
            <EyeIcon />
          </button>
        </div>
      </div>

      <div class="notification" v-show="message">
        {{ message }}
      </div>
      <button class="close" @click="$emit('close')">Закрыть</button>
    </div>

  </div>
</template>


<script setup>
import { nextTick, ref } from "vue";
import EyeIcon from '../assets/EyeIcon.vue';
import ModalImage from "./ModalImage.vue";
const props = defineProps({
  feature: Object
});
const emit = defineEmits(['close']);

const message = ref('');
let messageTimeout = null;

const imageSrc = ref('');
const showImageModal = ref(false);

const showMessageNoTimeout = (text) => {
  if (messageTimeout) {
    clearTimeout(messageTimeout);
    messageTimeout = null;
  }
  message.value = text;
};

const showMessageWithTimeout = (text) => {
  if (messageTimeout) clearTimeout(messageTimeout);
  message.value = text;
  messageTimeout = setTimeout(() => {
    message.value = '';
    messageTimeout = null;
  }, 3000);
};

async function generateMask() {
  if (!props.feature?.properties?.imagepath) {
    showMessageWithTimeout("Путь к изображению не найден");
    return;
  }

  const imagePath = props.feature.properties.imagepath;
  const url = `http://localhost:5269/api/Mask/create?folderPath=${encodeURIComponent(imagePath)}`;

  showMessageNoTimeout(`Выполняется процесс создания маски для: ${imagePath}`);
  await nextTick();
  await new Promise(resolve => setTimeout(resolve, 100));

  try {
    const response = await fetch(url);
    const text = await response.text();

    if (!response.ok) {
      showMessageNoTimeout(`Ошибка: ${text}`);
      return;
    }

    showMessageNoTimeout(`Маска успешно создана: ${text}`);
  } catch (error) {
    showMessageNoTimeout(`Ошибка при создании маски: ${error.message}`);
  }
}

async function detectFire() {
  if (!props.feature?.properties?.imagepath) {
    showMessageWithTimeout("Путь к изображению не найден");
    return;
  }

  const imagePath = props.feature.properties.imagepath;
  const url = `http://localhost:5269/api/FireMask/detect?maskPath=${encodeURIComponent(imagePath)}`;

  showMessageNoTimeout(`Выполняется процесс обнаружения пожара для: ${imagePath}`);
  await nextTick();
  await new Promise(resolve => setTimeout(resolve, 100));

  try {
    const response = await fetch(url);
    const data = await response.json();

    if (!response.ok) {
      showMessageNoTimeout(`Ошибка: ${JSON.stringify(data)}`);
      return;
    }

    const resultMessage = data.fire_detected
        ? "🔥 На снимке есть пожар!"
        : "✅ На снимке нет пожара!";

    showMessageNoTimeout(resultMessage);
  } catch (error) {
    showMessageNoTimeout(`Ошибка при запросе: ${error.message}`);
  }
}

async function combineBands() {
  if (!props.feature?.properties?.imagepath) {
    showMessageWithTimeout("Путь к изображению не найден");
    return;
  }

  const imagePath = props.feature.properties.imagepath;
  const url = `http://localhost:5269/api/Process/start?path=${encodeURIComponent(imagePath)}`;

  showMessageNoTimeout(`Выполняется процесс объединения слоев для: ${imagePath}`);
  await nextTick();
  await new Promise(resolve => setTimeout(resolve, 100));

  try {
    const response = await fetch(url);
    const result = await response.text();

    if (!response.ok) {
      if (response.status === 409) {
        showMessageNoTimeout("Фото уже объединено");
      } else {
        showMessageNoTimeout(`Ошибка: ${result}`);
      }
      return;
    }

    showMessageNoTimeout(`Слои объединены успешно: ${result}`);
  } catch (error) {
    showMessageNoTimeout(`Ошибка при запросе: ${error.message}`);
  }
}

async function checkImageExists(url) {
  try {
    const response = await fetch(url, { method: 'GET' });
    return response.ok && response.headers.get('content-type').startsWith('image');
  } catch {
    return false;
  }
}


async function viewFragment() {
  const productId = props.feature?.properties?.productid;
  if (!productId) {
    showMessageWithTimeout("productId не найден");
    return;
  }

  const url = `/${productId}_merged.png`;
  const exists = await checkImageExists(url);
  if (!exists) {
    showMessageWithTimeout("Снимок не найден");
    return;
  }

  imageSrc.value = url;
  showImageModal.value = true;
}

async function viewFragmentMask() {
  const productId = props.feature?.properties?.productid;
  if (!productId) {
    showMessageWithTimeout("productId не найден");
    return;
  }

  const url = `/${productId}_Voting.png`;
  const exists = await checkImageExists(url);
  if (!exists) {
    showMessageWithTimeout("Маска не найдена");
    return;
  }

  imageSrc.value = url;
  showImageModal.value = true;
}


</script>

<style scoped>
.notification {
  background-color: #e3f2fd;
  border-left: 4px solid #2196f3;
  padding: 10px;
  margin-top: 10px;
  color: #0d47a1;
  border-radius: 4px;
  font-size: 14px;
  margin-bottom: 10px;
}

.modal-backdrop {
  position: fixed;
  top: 0; left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}
.modal {
  background: white;
  padding: 20px 30px;
  border-radius: 8px;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 15px 0;
}

.action-button {
  min-width: 350px; /* или фиксированная ширина: width: 180px; */
  padding: 6px 12px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-align: center;
}

button {
  padding: 6px 12px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #1565c0;
}

.close {
  background: #aaa;
}

.close:hover {
  background-color: #d32f2f;
  color: white;
}

.action-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.eye-button {
  background-color: transparent;
  border: none;
  cursor: pointer;
  padding: 6px;
}
</style>
