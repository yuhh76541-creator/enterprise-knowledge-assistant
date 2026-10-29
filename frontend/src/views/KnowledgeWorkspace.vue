<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { api } from "../api/client";
import type { KnowledgeBase } from "../types";

const spaces = ref<KnowledgeBase[]>([]);
const connected = ref(false);
const loading = ref(true);
const submitting = ref(false);
const error = ref("");
const notice = ref("");
const name = ref("");
const description = ref("");
const canSubmit = computed(
  () => connected.value && name.value.trim().length > 0 && !submitting.value,
);

async function load(): Promise<void> {
  loading.value = true;
  error.value = "";
  try {
    const [health, items] = await Promise.all([api.health(), api.spaces()]);
    connected.value = health.status === "healthy";
    spaces.value = items;
  } catch (failure) {
    connected.value = false;
    error.value =
      failure instanceof Error ? failure.message : "加载失败，请重试。";
  } finally {
    loading.value = false;
  }
}

async function createSpace(): Promise<void> {
  if (!canSubmit.value) return;
  submitting.value = true;
  error.value = "";
  notice.value = "";
  try {
    const record = await api.createSpace(
      name.value.trim(),
      description.value.trim(),
    );
    spaces.value.unshift(record);
    name.value = "";
    description.value = "";
    notice.value = `已创建「${record.name}」`;
  } catch (failure) {
    error.value =
      failure instanceof Error ? failure.message : "创建失败，请重试。";
  } finally {
    submitting.value = false;
  }
}

function displayDate(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "long",
    day: "numeric",
  }).format(new Date(value));
}

onMounted(load);
</script>

<template>
  <div class="workspace">
    <aside class="sidebar">
      <a class="brand" href="/" aria-label="知序首页"
        ><span class="brand-symbol">知</span
        ><span>知序<small>KNOWLEDGE WORKSPACE</small></span></a
      >
      <p class="nav-label">工作空间</p>
      <a class="nav-item selected" href="#spaces"
        ><span>▦</span> 知识空间
        <span class="nav-count">{{ spaces.length }}</span></a
      >
      <div class="nav-item muted">
        <span>▤</span> 文档管理 <small>规划中</small>
      </div>
      <div class="nav-item muted">
        <span>◇</span> 智能问答 <small>规划中</small>
      </div>
      <div class="sidebar-note">
        <span class="tiny-line"></span>
        <p>让经验有处可寻，<br />让知识持续生长。</p>
        <small>本地工作台 · 基础框架 v0.1</small>
      </div>
    </aside>

    <main>
      <header class="topbar">
        <span>企业知识与业务助手</span
        ><span class="connection" :class="{ online: connected }"
          ><i></i
          >{{
            loading ? "正在连接" : connected ? "本机服务已连接" : "服务未连接"
          }}</span
        >
      </header>
      <div class="main-content">
        <section class="intro">
          <div>
            <p class="eyebrow">YOUR KNOWLEDGE, IN ORDER</p>
            <h1>为团队的知识，<br />建立一个清晰的起点。</h1>
            <p class="intro-copy">
              先创建知识空间，让制度、操作手册与业务经验各归其位。
            </p>
          </div>
          <div class="intro-mark" aria-hidden="true">
            <span class="sheet one"></span><span class="sheet two"></span
            ><span class="sheet three"><b>知</b><i></i><i></i><i></i></span
            ><span class="orbit">+</span>
          </div>
        </section>

        <div v-if="error" class="message error" role="alert">
          <span>{{ error }}</span
          ><button type="button" @click="load" :disabled="loading">
            重新连接
          </button>
        </div>
        <p v-if="notice" class="message success" role="status">{{ notice }}</p>

        <section id="spaces" class="spaces-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">KNOWLEDGE SPACES</p>
              <h2>
                我的知识空间 <span>{{ spaces.length }}</span>
              </h2>
            </div>
            <button
              class="text-button"
              type="button"
              @click="load"
              :disabled="loading"
            >
              {{ loading ? "正在刷新…" : "刷新列表 ↻" }}
            </button>
          </div>
          <div class="space-layout">
            <div class="spaces-panel" aria-live="polite" :aria-busy="loading">
              <div v-if="loading" class="empty-state">
                <span class="empty-symbol">⋯</span>
                <h3>正在连接知识空间</h3>
                <p>稍等片刻，读取本机保存的内容。</p>
              </div>
              <div v-else-if="!connected" class="empty-state">
                <span class="empty-symbol">↻</span>
                <h3>暂时无法读取知识空间</h3>
                <p>请启动本机服务后，点击重新连接。</p>
              </div>
              <div v-else-if="spaces.length === 0" class="empty-state">
                <span class="empty-symbol">▧</span>
                <h3>第一份知识，从这里开始</h3>
                <p>
                  创建一个空间，例如「IT 运维手册」或「业务制度」。<br />空间名称与说明将保存在本机。
                </p>
              </div>
              <article
                v-for="space in spaces"
                :key="space.id"
                class="space-card"
              >
                <div class="space-icon">▤</div>
                <div class="space-details">
                  <h3>{{ space.name }}</h3>
                  <p>{{ space.description || "还没有添加空间说明" }}</p>
                  <span>创建于 {{ displayDate(space.created_at) }}</span>
                </div>
                <span class="space-badge">已创建</span>
              </article>
            </div>
            <form class="create-panel" @submit.prevent="createSpace">
              <span class="form-icon">＋</span>
              <h3>创建知识空间</h3>
              <p>按业务主题整理，查找更有条理。</p>
              <label for="space-name">空间名称 <span>必填</span></label
              ><input
                id="space-name"
                v-model="name"
                maxlength="80"
                placeholder="例如：IT 运维手册"
                required
              /><label for="space-description">空间说明 <span>选填</span></label
              ><textarea
                id="space-description"
                v-model="description"
                maxlength="500"
                rows="3"
                placeholder="这个空间将整理哪些内容？"
              ></textarea
              ><button
                class="primary-button"
                :disabled="!canSubmit"
                type="submit"
              >
                {{ submitting ? "正在创建…" : "创建空间" }}
                <span>↗</span></button
              ><small>仅创建空间，暂不上传文件或调用模型。</small>
            </form>
          </div>
        </section>

        <section class="next-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">WHAT COMES NEXT</p>
              <h2>接下来，让知识真正流动</h2>
            </div>
            <span class="phase-badge">后续开发计划</span>
          </div>
          <div class="feature-grid">
            <article>
              <span>01 / 文档入库</span>
              <h3>从资料到知识</h3>
              <p>导入文档、提取正文，按空间构建可检索的知识内容。</p>
              <small>规划中</small>
            </article>
            <article>
              <span>02 / 检索问答</span>
              <h3>带着出处回答</h3>
              <p>结合资料生成回答，展示引用片段，让结果便于核对。</p>
              <small>规划中</small>
            </article>
            <article>
              <span>03 / 业务辅助</span>
              <h3>让经验参与工作</h3>
              <p>围绕常见 IT 问题提供资料与排查步骤参考。</p>
              <small>规划中</small>
            </article>
          </div>
        </section>
        <footer>
          知序 · 企业级智能知识库与业务助手平台
          <span>基础框架 / 持续构建中</span>
        </footer>
      </div>
    </main>
  </div>
</template>
