class EnterpriseConfig:
    # Sustituye los '0000000000000' por tus 13 dígitos reales de tu Avis d'imposition
    FISCAL_ID = "0000000000000"
    SIRET = "94361019600017"
    TVA_INTRA = "FR74943610196"

    @classmethod
    def get_full_identity(cls):
        return {
            "siret": cls.SIRET,
            "fiscal_id": cls.FISCAL_ID,
            "tva": cls.TVA_INTRA
        }
