"""
Service de parsing de fichiers (CSV, PDF, Excel)
"""
import pandas as pd
import PyPDF2
import pdfplumber
from typing import List, Dict, Optional, Union
import logging
from datetime import datetime
import io
from app.models.models import EvaluationCreate

logger = logging.getLogger(__name__)


class FileParser:
    """
    Parser pour différents formats de fichiers d'évaluation
    """
    
    # Colonnes requises et leurs aliases possibles
    REQUIRED_COLUMNS = {
        'evaluation_id': ['evaluation_id', 'eval_id', 'id'],
        'formation_id': ['formation_id', 'form_id', 'formation'],
        'type_formation': ['type_formation', 'formation_type', 'type'],
        'formateur_id': ['formateur_id', 'formateur', 'trainer_id'],
        'satisfaction': ['satisfaction', 'sat'],
        'contenu': ['contenu', 'content', 'cont'],
        'logistique': ['logistique', 'logistics', 'log'],
        'applicabilite': ['applicabilite', 'applicability', 'app'],
        'commentaire': ['commentaire', 'comment', 'comments', 'feedback'],
        'langue': ['langue', 'language', 'lang'],
        'date': ['date', 'evaluation_date', 'eval_date'],
    }
    
    @classmethod
    def parse_csv(cls, file_content: Union[bytes, str], filename: str) -> List[EvaluationCreate]:
        """
        Parse un fichier CSV
        
        Args:
            file_content: Contenu du fichier (bytes ou string)
            filename: Nom du fichier
            
        Returns:
            Liste d'objets EvaluationCreate
        """
        try:
            # Lire le CSV
            if isinstance(file_content, bytes):
                df = pd.read_csv(io.BytesIO(file_content))
            else:
                df = pd.read_csv(io.StringIO(file_content))
            
            # Normaliser les noms de colonnes
            df = cls._normalize_columns(df)
            
            # Valider les colonnes requises
            cls._validate_columns(df)
            
            # Convertir en liste d'évaluations
            evaluations = []
            for idx, row in df.iterrows():
                try:
                    eval_data = cls._row_to_evaluation(row, filename)
                    evaluations.append(eval_data)
                except Exception as e:
                    logger.warning(f"Error parsing row {idx}: {e}")
                    continue
            
            logger.info(f"Parsed {len(evaluations)} evaluations from CSV")
            return evaluations
            
        except Exception as e:
            logger.error(f"Error parsing CSV file: {e}")
            raise ValueError(f"Invalid CSV format: {e}")
    
    @classmethod
    def parse_excel(cls, file_content: bytes, filename: str) -> List[EvaluationCreate]:
        """
        Parse un fichier Excel
        
        Args:
            file_content: Contenu du fichier
            filename: Nom du fichier
            
        Returns:
            Liste d'objets EvaluationCreate
        """
        try:
            # Lire le fichier Excel
            df = pd.read_excel(io.BytesIO(file_content))
            
            # Normaliser les noms de colonnes
            df = cls._normalize_columns(df)
            
            # Valider les colonnes requises
            cls._validate_columns(df)
            
            # Convertir en liste d'évaluations
            evaluations = []
            for idx, row in df.iterrows():
                try:
                    eval_data = cls._row_to_evaluation(row, filename)
                    evaluations.append(eval_data)
                except Exception as e:
                    logger.warning(f"Error parsing row {idx}: {e}")
                    continue
            
            logger.info(f"Parsed {len(evaluations)} evaluations from Excel")
            return evaluations
            
        except Exception as e:
            logger.error(f"Error parsing Excel file: {e}")
            raise ValueError(f"Invalid Excel format: {e}")
    
    @classmethod
    def parse_pdf(cls, file_content: bytes, filename: str) -> List[EvaluationCreate]:
        """
        Parse un fichier PDF (tables extraites)
        
        Args:
            file_content: Contenu du fichier
            filename: Nom du fichier
            
        Returns:
            Liste d'objets EvaluationCreate
        """
        try:
            evaluations = []
            
            # Essayer avec pdfplumber pour extraire les tables
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                all_tables = []
                
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        all_tables.extend(tables)
                
                if not all_tables:
                    raise ValueError("No tables found in PDF")
                
                # Convertir la première table en DataFrame
                # Supposer que la première ligne est l'en-tête
                for table in all_tables:
                    if len(table) < 2:
                        continue
                    
                    df = pd.DataFrame(table[1:], columns=table[0])
                    
                    # Normaliser et valider
                    df = cls._normalize_columns(df)
                    
                    try:
                        cls._validate_columns(df)
                    except ValueError:
                        # Cette table n'a pas le bon format
                        continue
                    
                    # Convertir en évaluations
                    for idx, row in df.iterrows():
                        try:
                            eval_data = cls._row_to_evaluation(row, filename)
                            evaluations.append(eval_data)
                        except Exception as e:
                            logger.warning(f"Error parsing PDF row {idx}: {e}")
                            continue
            
            if not evaluations:
                raise ValueError("No valid evaluation data found in PDF")
            
            logger.info(f"Parsed {len(evaluations)} evaluations from PDF")
            return evaluations
            
        except Exception as e:
            logger.error(f"Error parsing PDF file: {e}")
            raise ValueError(f"Invalid PDF format: {e}")
    
    @classmethod
    def _normalize_columns(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalise les noms de colonnes selon les aliases
        
        Args:
            df: DataFrame à normaliser
            
        Returns:
            DataFrame avec colonnes normalisées
        """
        # Convertir les noms en minuscules et supprimer espaces
        df.columns = df.columns.str.lower().str.strip()
        
        # Mapper les aliases vers les noms standards
        column_mapping = {}
        for standard_name, aliases in cls.REQUIRED_COLUMNS.items():
            for col in df.columns:
                if col in aliases:
                    column_mapping[col] = standard_name
                    break
        
        df = df.rename(columns=column_mapping)
        return df
    
    @classmethod
    def _validate_columns(cls, df: pd.DataFrame) -> None:
        """
        Valide que toutes les colonnes requises sont présentes
        
        Args:
            df: DataFrame à valider
            
        Raises:
            ValueError: Si des colonnes manquent
        """
        required = set(cls.REQUIRED_COLUMNS.keys())
        present = set(df.columns)
        missing = required - present
        
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    
    @classmethod
    def _row_to_evaluation(cls, row: pd.Series, source_file: str) -> EvaluationCreate:
        """
        Convertit une ligne en EvaluationCreate
        
        Args:
            row: Ligne du DataFrame
            source_file: Nom du fichier source
            
        Returns:
            Objet EvaluationCreate
        """
        # Gérer la date
        date_val = row.get('date')
        if pd.isna(date_val):
            date_obj = datetime.utcnow()
        elif isinstance(date_val, datetime):
            date_obj = date_val
        elif isinstance(date_val, str):
            try:
                date_obj = pd.to_datetime(date_val)
            except:
                date_obj = datetime.utcnow()
        else:
            date_obj = datetime.utcnow()
        
        # Convertir les scores en entiers
        def to_int(val, default=3):
            try:
                return int(float(val)) if not pd.isna(val) else default
            except:
                return default
        
        return EvaluationCreate(
            evaluation_id=str(row['evaluation_id']),
            formation_id=str(row['formation_id']),
            type_formation=str(row['type_formation']),
            formateur_id=str(row['formateur_id']),
            satisfaction=to_int(row['satisfaction']),
            contenu=to_int(row['contenu']),
            logistique=to_int(row['logistique']),
            applicabilite=to_int(row['applicabilite']),
            commentaire=str(row['commentaire']) if not pd.isna(row['commentaire']) else "",
            langue=str(row.get('langue', 'FR')) if not pd.isna(row.get('langue')) else None,
            date=date_obj
        )
    
    @classmethod
    def parse_file(cls, file_content: bytes, filename: str) -> List[EvaluationCreate]:
        """
        Parse un fichier selon son extension
        
        Args:
            file_content: Contenu du fichier
            filename: Nom du fichier
            
        Returns:
            Liste d'objets EvaluationCreate
        """
        extension = filename.lower().split('.')[-1]
        
        if extension == 'csv':
            return cls.parse_csv(file_content, filename)
        elif extension in ['xlsx', 'xls']:
            return cls.parse_excel(file_content, filename)
        elif extension == 'pdf':
            return cls.parse_pdf(file_content, filename)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
