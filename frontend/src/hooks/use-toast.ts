/**
 * Toast hook using sonner
 * Provides a consistent API for toast notifications
 */

import { toast as sonnerToast } from 'sonner';

interface ToastOptions {
  title?: string;
  description?: string;
  variant?: 'default' | 'destructive';
  action?: React.ReactNode;
}

export function useToast() {
  const toast = ({ title, description, variant = 'default' }: ToastOptions) => {
    const message = title || '';
    const descriptionText = description || '';

    if (variant === 'destructive') {
      return sonnerToast.error(message, {
        description: descriptionText,
      });
    }

    return sonnerToast.success(message, {
      description: descriptionText,
    });
  };

  return {
    toast,
  };
}
