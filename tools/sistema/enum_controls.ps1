<# 平铺枚举目标进程所有顶层窗口 + 子控件（类名/文本/矩形/hwnd/id）。
   注意：EnumChildWindows 本身会递归遍历全部后代，回调里不要再递归，否则数量指数爆炸。 #>
$ProcessName = 'SISTEMA'
$OutFile = 'C:\Users\sf-bc04.SF\Documents\deepseek-harness\default-workspace\_controls.txt'

Add-Type @"
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public class WFlat {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr parent, EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern int GetDlgCtrlID(IntPtr h);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }

  public static string Info(IntPtr h) {
    var cls = new StringBuilder(256); GetClassName(h, cls, 256);
    var txt = new StringBuilder(512); GetWindowText(h, txt, 512);
    RECT r; GetWindowRect(h, out r);
    return string.Format("{0} | hwnd=0x{1:X} | id={2} | vis={3} | ({4},{5})-({6},{7}) | '{8}'",
      cls.ToString(), h.ToInt64(), GetDlgCtrlID(h), IsWindowVisible(h),
      r.Left, r.Top, r.Right, r.Bottom,
      txt.ToString().Replace("\r", " ").Replace("\n", " ").Trim());
  }
  public static List<string> Children(IntPtr root) {
    var res = new List<string>();
    EnumChildWindows(root, (h, l) => { res.Add(Info(h)); return true; }, IntPtr.Zero);
    return res;
  }
}
"@

$proc = Get-Process $ProcessName | Select-Object -First 1
$pid32 = [uint32]$proc.Id
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("process $ProcessName pid=$pid32")

$cb = [WFlat+EnumProc]{
  param($h, $l)
  $p = [uint32]0
  [WFlat]::GetWindowThreadProcessId($h, [ref]$p) | Out-Null
  if ($p -eq $pid32 -and [WFlat]::IsWindowVisible($h)) {
    $lines.Add('')
    $lines.Add("=== TOP-LEVEL " + [WFlat]::Info($h) + " ===")
    [WFlat]::Children($h) | ForEach-Object { $lines.Add('  ' + $_) }
  }
  return $true
}
[WFlat]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null

$lines | Set-Content -Path $OutFile -Encoding utf8
Write-Output "wrote $OutFile ($($lines.Count) lines)"
