<template>
  <div style="margin-bottom: 8px;">
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px; border-bottom: 1px solid var(--divider-color);">
      <div>
        <strong>{{ category.name }}</strong>
        <span style="margin-left: 8px; font-size: 12px; color: var(--text-secondary);">
          {{ category.item_count }} items
        </span>
      </div>
      <button @click="$emit('delete', category.id)" style="color: var(--error-color); background: none; border: none; cursor: pointer; padding: 4px 8px;">
        Delete
      </button>
    </div>
    <div v-if="category.children && category.children.length > 0" style="margin-left: 24px;">
      <CategoryTreeItem
        v-for="child in category.children"
        :key="child.id"
        :category="child"
        @delete="$emit('delete', $event)"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'CategoryTreeItem',
  props: {
    category: {
      type: Object,
      required: true
    }
  },
  emits: ['delete']
}
</script>
