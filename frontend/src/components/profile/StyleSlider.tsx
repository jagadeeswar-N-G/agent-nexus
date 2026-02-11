"use client";

interface StyleSliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  leftLabel: string;
  rightLabel: string;
}

export function StyleSlider({
  label,
  value,
  onChange,
  leftLabel,
  rightLabel,
}: StyleSliderProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium">{label}</label>
        <span className="text-sm text-muted-foreground">{value}</span>
      </div>

      <input
        type="range"
        min="0"
        max="100"
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full accent-primary"
      />

      <div className="flex justify-between text-xs text-muted-foreground">
        <span>{leftLabel}</span>
        <span>{rightLabel}</span>
      </div>
    </div>
  );
}
