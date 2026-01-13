<template>
  <div style="margin-bottom: 8px;">
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px; border-bottom: 1px solid var(--divider-color);">
      <div>
        <strong>{{ location.name }}</strong>
        <span style="margin-left: 8px; font-size: 12px; color: var(--text-secondary);">
          ({{ location.location_type }}) • {{ location.item_count }} items
        </span>
      </div>
      <button @click="$emit('delete', location.id)" style="color: var(--error-color); background: none; border: none; cursor: pointer; padding: 4px 8px;">
        Delete
      </button>
    </div>
    <div v-if="location.children && location.children.length > 0" style="margin-left: 24px;">
      <LocationTreeItem
        v-for="child in location.children"
        :key="child.id"
        :location="child"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'LocationTreeItem',
  props: {
    location: {
      type: Object,
      required: true
    }
  },
  emits: ['edit', 'delete']
}
</script>
