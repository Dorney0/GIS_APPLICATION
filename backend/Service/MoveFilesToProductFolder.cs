using System;
using System.IO;

namespace backend.Service
{
    public class MoveFilesToProductFolder
    {
        private readonly string _basePath = @"D:\GIS_APPLICATION\geo-images";

        public string MoveFiles(string sourceFolderPath, string productId)
        {
            if (string.IsNullOrEmpty(sourceFolderPath))
                throw new ArgumentException("Source folder path is null or empty", nameof(sourceFolderPath));
            if (string.IsNullOrEmpty(productId))
                throw new ArgumentException("ProductId is null or empty", nameof(productId));
            
            if (!Directory.Exists(sourceFolderPath))
                throw new DirectoryNotFoundException($"Source folder does not exist: {sourceFolderPath}");

            string destFolder = Path.Combine(_basePath, productId);
            if (!Directory.Exists(destFolder))
            {
                Directory.CreateDirectory(destFolder);
            }

            // Перемещаем все файлы из sourceFolderPath в destFolder
            var files = Directory.GetFiles(sourceFolderPath, "*", SearchOption.AllDirectories);
            foreach (var filePath in files)
            {
                string fileName = Path.GetFileName(filePath);
                string destPath = Path.Combine(destFolder, fileName);

                // Если файл с таким именем уже есть, можно перезаписать или изменить логику
                if (File.Exists(destPath))
                {
                    File.Delete(destPath); // удаляем старый, если нужно
                }

                File.Move(filePath, destPath);
            }

            return destFolder; // ✅ добавляем возврат
        }
    }
}