export function convertEpochToLocalDateString(epochTime) {
    const date = new Date(epochTime * 1000); // Date ctor takes milliseconds
    const day = date.getUTCDate().toString().padStart(2, '0');
    const month = (date.getUTCMonth() + 1).toString().padStart(2, '0'); // utc month is 0-11
    const year = date.getUTCFullYear().toString();
    const hour = date.getUTCHours().toString().padStart(2, '0');
    const minute = date.getUTCMinutes().toString().padStart(2, '0');
    const second = date.getUTCSeconds().toString().padStart(2, '0');
  
    return `${year}/${month}/${day}, ${hour}:${minute}:${second}`;
}
