import pandas as pd
import os
from typing import Dict, Any, List
from pathlib import Path

from app.core.logging_config import get_logger


logger = get_logger(__name__)


class ExcelOperationTask:
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls', '.csv']
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        operation = parameters.get("operation", "organize")
        file_path = parameters.get("file_path")
        
        if not file_path:
            return {
                "success": False,
                "message": "No Excel file specified"
            }
        
        if not self._is_excel_file(file_path):
            return {
                "success": False,
                "message": "File is not a supported Excel format"
            }
        
        try:
            if operation == "remove_duplicates":
                return await self._remove_duplicates(file_path)
            elif operation == "sort_alphabetical":
                return await self._sort_alphabetical(file_path)
            elif operation == "organize":
                return await self._organize_data(file_path)
            elif operation == "clean_data":
                return await self._clean_data(file_path)
            else:
                return {
                    "success": False,
                    "message": f"Unknown Excel operation: {operation}"
                }
        except Exception as e:
            logger.error(f"Excel operation failed: {e}")
            return {
                "success": False,
                "message": f"Error processing Excel file: {str(e)}"
            }
    
    def _is_excel_file(self, file_path: str) -> bool:
        return any(file_path.lower().endswith(ext) for ext in self.supported_formats)
    
    async def _remove_duplicates(self, file_path: str) -> Dict[str, Any]:
        try:
            df = pd.read_excel(file_path) if file_path.endswith(('.xlsx', '.xls')) else pd.read_csv(file_path)
            
            original_count = len(df)
            df_cleaned = df.drop_duplicates()
            removed_count = original_count - len(df_cleaned)
            
            output_path = self._get_output_path(file_path, "_no_duplicates")
            
            if file_path.endswith(('.xlsx', '.xls')):
                df_cleaned.to_excel(output_path, index=False)
            else:
                df_cleaned.to_csv(output_path, index=False)
            
            return {
                "success": True,
                "message": f"Removed {removed_count} duplicate rows. Saved to {output_path}",
                "original_rows": original_count,
                "remaining_rows": len(df_cleaned),
                "removed_duplicates": removed_count,
                "output_file": output_path
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to remove duplicates: {str(e)}"
            }
    
    async def _sort_alphabetical(self, file_path: str) -> Dict[str, Any]:
        try:
            df = pd.read_excel(file_path) if file_path.endswith(('.xlsx', '.xls')) else pd.read_csv(file_path)
            
            text_columns = df.select_dtypes(include=['object']).columns
            
            if len(text_columns) == 0:
                return {
                    "success": False,
                    "message": "No text columns found for alphabetical sorting"
                }
            
            primary_column = text_columns[0]
            df_sorted = df.sort_values(by=primary_column, ascending=True)
            
            output_path = self._get_output_path(file_path, "_sorted")
            
            if file_path.endswith(('.xlsx', '.xls')):
                df_sorted.to_excel(output_path, index=False)
            else:
                df_sorted.to_csv(output_path, index=False)
            
            return {
                "success": True,
                "message": f"Sorted data alphabetically by '{primary_column}'. Saved to {output_path}",
                "sorted_by": primary_column,
                "total_rows": len(df_sorted),
                "output_file": output_path
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to sort alphabetically: {str(e)}"
            }
    
    async def _organize_data(self, file_path: str) -> Dict[str, Any]:
        try:
            df = pd.read_excel(file_path) if file_path.endswith(('.xlsx', '.xls')) else pd.read_csv(file_path)
            
            original_count = len(df)
            
            df_cleaned = df.drop_duplicates()
            removed_count = original_count - len(df_cleaned)
            
            text_columns = df_cleaned.select_dtypes(include=['object']).columns
            if len(text_columns) > 0:
                primary_column = text_columns[0]
                df_organized = df_cleaned.sort_values(by=primary_column, ascending=True)
            else:
                df_organized = df_cleaned
            
            output_path = self._get_output_path(file_path, "_organized")
            
            if file_path.endswith(('.xlsx', '.xls')):
                df_organized.to_excel(output_path, index=False)
            else:
                df_organized.to_csv(output_path, index=False)
            
            return {
                "success": True,
                "message": f"Organized Excel data: removed {removed_count} duplicates and sorted alphabetically. Saved to {output_path}",
                "original_rows": original_count,
                "final_rows": len(df_organized),
                "removed_duplicates": removed_count,
                "sorted_by": text_columns[0] if len(text_columns) > 0 else "N/A",
                "output_file": output_path
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to organize data: {str(e)}"
            }
    
    async def _clean_data(self, file_path: str) -> Dict[str, Any]:
        try:
            df = pd.read_excel(file_path) if file_path.endswith(('.xlsx', '.xls')) else pd.read_csv(file_path)
            
            original_count = len(df)
            
            df_cleaned = df.drop_duplicates()
            df_cleaned = df_cleaned.dropna()
            
            removed_duplicates = original_count - len(df_cleaned)
            removed_empty = len(df) - len(df_cleaned)
            
            text_columns = df_cleaned.select_dtypes(include=['object']).columns
            if len(text_columns) > 0:
                primary_column = text_columns[0]
                df_final = df_cleaned.sort_values(by=primary_column, ascending=True)
            else:
                df_final = df_cleaned
            
            output_path = self._get_output_path(file_path, "_cleaned")
            
            if file_path.endswith(('.xlsx', '.xls')):
                df_final.to_excel(output_path, index=False)
            else:
                df_final.to_csv(output_path, index=False)
            
            return {
                "success": True,
                "message": f"Cleaned Excel data: removed {removed_duplicates} duplicates, {removed_empty} empty rows, and sorted alphabetically. Saved to {output_path}",
                "original_rows": original_count,
                "final_rows": len(df_final),
                "removed_duplicates": removed_duplicates,
                "removed_empty": removed_empty,
                "sorted_by": text_columns[0] if len(text_columns) > 0 else "N/A",
                "output_file": output_path
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to clean data: {str(e)}"
            }
    
    def _get_output_path(self, original_path: str, suffix: str) -> str:
        path = Path(original_path)
        return str(path.parent / f"{path.stem}{suffix}{path.suffix}")
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        try:
            df = pd.read_excel(file_path) if file_path.endswith(('.xlsx', '.xls')) else pd.read_csv(file_path)
            
            return {
                "success": True,
                "file_path": file_path,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "column_names": list(df.columns),
                "data_types": df.dtypes.to_dict(),
                "has_duplicates": len(df) != len(df.drop_duplicates()),
                "has_empty_cells": df.isnull().any().any(),
                "file_size": os.path.getsize(file_path)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to read file info: {str(e)}"
            }
