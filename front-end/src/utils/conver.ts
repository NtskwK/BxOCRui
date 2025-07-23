export function dateConver(dateStr: string): Date | undefined {
  // 解析 YYYYMMDD 格式日期的函数
  if (!dateStr) return undefined;

  // 如果是 YYYYMMDD 格式 (8位数字)
  if (/^\d{8}$/.test(dateStr)) {
    const year = dateStr.substring(0, 4);
    const month = dateStr.substring(4, 6);
    const day = dateStr.substring(6, 8);

    // 创建日期对象 (月份需要减1，因为JavaScript月份从0开始)
    const parsedDate = new Date(
      parseInt(year),
      parseInt(month) - 1,
      parseInt(day)
    );

    // 验证日期是否有效
    if (isNaN(parsedDate.getTime())) {
      console.warn(`Invalid date: ${dateStr}`);
      return undefined;
    }

    return parsedDate;
  }

  // 尝试其他格式的日期解析
  const parsedDate = new Date(dateStr);
  return isNaN(parsedDate.getTime()) ? undefined : parsedDate;
}

export function updateDateFromStr(dataStr: string | undefined, defaultDate: Date): Date {
  if (!dataStr) return defaultDate;
  const parsedDate = dateConver(dataStr);
  if (!parsedDate) return defaultDate;
  return parsedDate;
}
