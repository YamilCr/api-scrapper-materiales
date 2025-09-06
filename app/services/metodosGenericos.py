def ordenar_por_campo(lista, campo, descendente=False):
    """
    Ordena una lista de objetos (dicts) por el campo especificado.
    Si el campo no existe o es None, lo pone al final.
    """
    def clave(obj):
        valor = obj.get(campo)
        if isinstance(valor, str) and valor.replace(".", "").isdigit():
            return float(valor.replace(".", ""))
        return valor if valor is not None else float('inf') if not descendente else float('-inf')

    return sorted(lista, key=clave, reverse=descendente)

