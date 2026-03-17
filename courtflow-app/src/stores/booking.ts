import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { AvailabilityGrid, SlotInfo, HoldSlotOut } from "../types";
import { getAvailability } from "../api/venues";
import { holdSlots, releaseHold } from "../api/bookings";

interface SelectedSlot {
  courtId: string;
  slotStart: string;
  slotEnd: string;
  amountCents: number;
}

export const useBookingStore = defineStore("booking", () => {
  const venueId = ref<string | null>(null);
  const currentDate = ref<string>(""); // YYYY-MM-DD
  const grid = ref<AvailabilityGrid>({});
  const gridLoading = ref(false);

  // Client-side selection (pre-hold)
  const selectedSlots = ref<Map<string, SelectedSlot>>(new Map());

  // Active holds (after server responds)
  const activeHolds = ref<HoldSlotOut[]>([]);

  const totalCents = computed(() =>
    Array.from(selectedSlots.value.values()).reduce(
      (sum, s) => sum + s.amountCents,
      0,
    ),
  );

  const selectedCount = computed(() => selectedSlots.value.size);

  function slotKey(courtId: string, slotStart: string) {
    return `${courtId}::${slotStart}`;
  }

  function isSelected(courtId: string, slotStart: string): boolean {
    return selectedSlots.value.has(slotKey(courtId, slotStart));
  }

  function toggleSlot(slot: SlotInfo) {
    if (
      slot.status !== "available" &&
      !isSelected(slot.court_id, slot.slot_start)
    )
      return;
    const key = slotKey(slot.court_id, slot.slot_start);
    if (selectedSlots.value.has(key)) {
      selectedSlots.value.delete(key);
    } else {
      selectedSlots.value.set(key, {
        courtId: slot.court_id,
        slotStart: slot.slot_start,
        slotEnd: slot.slot_end,
        amountCents: slot.amount_cents!,
      });
    }
  }

  async function loadGrid(vid: string, date: string) {
    venueId.value = vid;
    currentDate.value = date;
    gridLoading.value = true;
    try {
      grid.value = await getAvailability(vid, date);
    } finally {
      gridLoading.value = false;
    }
  }

  async function submitHold(contactPhone?: string): Promise<HoldSlotOut[]> {
    if (!venueId.value || selectedSlots.value.size === 0) return [];
    const slots = Array.from(selectedSlots.value.values()).map((s) => ({
      court_id: s.courtId,
      slot_start: s.slotStart,
      slot_end: s.slotEnd,
    }));
    const resp = await holdSlots({
      venue_id: venueId.value,
      slots,
      contact_phone: contactPhone,
    });
    activeHolds.value = resp.holds;
    selectedSlots.value.clear();
    return resp.holds;
  }

  async function clearHolds() {
    for (const hold of activeHolds.value) {
      await releaseHold(hold.reservation_id).catch(() => {});
    }
    activeHolds.value = [];
  }

  function clearSelection() {
    selectedSlots.value.clear();
  }

  function reset() {
    selectedSlots.value.clear();
    activeHolds.value = [];
    grid.value = {};
  }

  return {
    venueId,
    currentDate,
    grid,
    gridLoading,
    selectedSlots,
    activeHolds,
    totalCents,
    selectedCount,
    isSelected,
    toggleSlot,
    loadGrid,
    submitHold,
    clearHolds,
    clearSelection,
    reset,
  };
});
