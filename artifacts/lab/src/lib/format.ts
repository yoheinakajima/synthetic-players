import { format, parseISO } from 'date-fns';

export function formatDate(dateString: string | undefined | null) {
  if (!dateString) return '—';
  try {
    return format(parseISO(dateString), 'MMM d, yyyy');
  } catch (e) {
    return dateString;
  }
}

export function formatDateTime(dateString: string | undefined | null) {
  if (!dateString) return '—';
  try {
    return format(parseISO(dateString), 'MMM d, yyyy HH:mm');
  } catch (e) {
    return dateString;
  }
}

export function formatPercent(value: number | undefined | null) {
  if (value === undefined || value === null) return '—';
  return `${(value * 100).toFixed(1)}%`;
}

export function formatNumber(value: number | undefined | null, decimals = 2) {
  if (value === undefined || value === null) return '—';
  return value.toFixed(decimals);
}
