import re
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional


@dataclass
class Finding:
    rule_id: str
    title: str
    severity: str
    category: str
    line: int
    function: Optional[str]
    snippet: str
    description: str
    recommendation: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


RULES = [
    {
        "rule_id": "SG001",
        "title": "Versión antigua de Solidity",
        "severity": "LOW",
        "category": "Compatibilidad",
    },
    {
        "rule_id": "SG002",
        "title": "Uso de tx.origin",
        "severity": "MEDIUM",
        "category": "Control de acceso",
    },
    {
        "rule_id": "SG003",
        "title": "Uso de selfdestruct",
        "severity": "MEDIUM",
        "category": "Operación sensible",
    },
    {
        "rule_id": "SG004",
        "title": "Posible patrón de reentrancy",
        "severity": "HIGH",
        "category": "Llamadas externas",
    },
    {
        "rule_id": "SG005",
        "title": "Resultado de llamada de bajo nivel no verificado",
        "severity": "MEDIUM",
        "category": "Manejo de errores",
    },
    {
        "rule_id": "SG006",
        "title": "Uso de delegatecall",
        "severity": "MEDIUM",
        "category": "Ejecución externa",
    },
    {
        "rule_id": "SG007",
        "title": "Dependencia temporal con block.timestamp",
        "severity": "LOW",
        "category": "Lógica temporal",
    },
    {
        "rule_id": "SG008",
        "title": "Aleatoriedad basada en variables de bloque",
        "severity": "MEDIUM",
        "category": "Aleatoriedad",
    },
]


class SmartContractAnalyzer:
    """Analizador educativo y heurístico de contratos Solidity.

    SmartGuard no determina si un contrato es seguro. Identifica patrones
    predefinidos para apoyar una revisión inicial del código fuente.
    """

    def analyze(self, source_code: str) -> List[dict]:
        if not isinstance(source_code, str):
            raise TypeError("source_code debe ser texto")

        original_lines = source_code.splitlines()
        clean_lines = self._strip_comments_preserve_lines(source_code).splitlines()
        function_map = self._build_function_map(clean_lines)
        findings: List[Finding] = []

        findings.extend(self._check_old_solidity_version(clean_lines, original_lines, function_map))
        findings.extend(self._check_tx_origin(clean_lines, original_lines, function_map))
        findings.extend(self._check_selfdestruct(clean_lines, original_lines, function_map))
        findings.extend(self._check_possible_reentrancy(clean_lines, original_lines, function_map))
        findings.extend(self._check_unchecked_low_level_call(clean_lines, original_lines, function_map))
        findings.extend(self._check_delegatecall(clean_lines, original_lines, function_map))
        findings.extend(self._check_timestamp_dependency(clean_lines, original_lines, function_map))
        findings.extend(self._check_weak_randomness(clean_lines, original_lines, function_map))

        severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        findings.sort(key=lambda item: (severity_order.get(item.severity, 99), item.line, item.rule_id))
        return [finding.to_dict() for finding in findings]

    @staticmethod
    def get_rules() -> List[Dict[str, str]]:
        return RULES

    @staticmethod
    def _strip_comments_preserve_lines(source_code: str) -> str:
        """Elimina comentarios // y /* */ sin cambiar el número de líneas."""
        result: List[str] = []
        i = 0
        in_block = False
        while i < len(source_code):
            if in_block:
                if source_code.startswith("*/", i):
                    in_block = False
                    result.extend("  ")
                    i += 2
                elif source_code[i] == "\n":
                    result.append("\n")
                    i += 1
                else:
                    result.append(" ")
                    i += 1
                continue

            if source_code.startswith("/*", i):
                in_block = True
                result.extend("  ")
                i += 2
            elif source_code.startswith("//", i):
                while i < len(source_code) and source_code[i] != "\n":
                    result.append(" ")
                    i += 1
            else:
                result.append(source_code[i])
                i += 1
        return "".join(result)

    @staticmethod
    def _build_function_map(lines: List[str]) -> Dict[int, Optional[str]]:
        function_pattern = re.compile(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
        mapping: Dict[int, Optional[str]] = {}
        current_function: Optional[str] = None
        brace_depth = 0
        function_start_depth: Optional[int] = None

        for index, line in enumerate(lines, start=1):
            match = function_pattern.search(line)
            if match:
                current_function = match.group(1)
                function_start_depth = brace_depth + line[: match.end()].count("{")

            mapping[index] = current_function
            brace_depth += line.count("{") - line.count("}")

            if current_function is not None and function_start_depth is not None:
                if brace_depth < function_start_depth:
                    current_function = None
                    function_start_depth = None
        return mapping

    @staticmethod
    def _snippet(original_lines: List[str], line_number: int) -> str:
        if 1 <= line_number <= len(original_lines):
            return original_lines[line_number - 1].strip()
        return ""

    def _finding(
        self,
        *,
        rule_id: str,
        title: str,
        severity: str,
        category: str,
        line: int,
        original_lines: List[str],
        function_map: Dict[int, Optional[str]],
        description: str,
        recommendation: str,
    ) -> Finding:
        return Finding(
            rule_id=rule_id,
            title=title,
            severity=severity,
            category=category,
            line=line,
            function=function_map.get(line),
            snippet=self._snippet(original_lines, line),
            description=description,
            recommendation=recommendation,
        )

    def _check_old_solidity_version(self, lines, original_lines, function_map):
        findings = []
        pattern = re.compile(r"pragma\s+solidity\s+[^0-9]*([0-9]+)\.([0-9]+)\.([0-9]+)")
        for index, line in enumerate(lines, start=1):
            match = pattern.search(line)
            if not match:
                continue
            major, minor, _patch = map(int, match.groups())
            if major == 0 and minor < 8:
                findings.append(self._finding(
                    rule_id="SG001", title="Versión antigua de Solidity", severity="LOW",
                    category="Compatibilidad", line=index, original_lines=original_lines,
                    function_map=function_map,
                    description=("El contrato declara una versión anterior a Solidity 0.8.x. "
                                 "SmartGuard la marca como una señal de revisión para este prototipo."),
                    recommendation=("Revisar compatibilidad y considerar una versión moderna antes "
                                    "de desplegar el contrato."),
                ))
        return findings

    def _check_tx_origin(self, lines, original_lines, function_map):
        findings = []
        for index, line in enumerate(lines, start=1):
            if "tx.origin" in line:
                findings.append(self._finding(
                    rule_id="SG002", title="Uso de tx.origin", severity="MEDIUM",
                    category="Control de acceso", line=index, original_lines=original_lines,
                    function_map=function_map,
                    description=("Se detectó tx.origin. Si se utiliza para autorización, puede "
                                 "generar una lógica de permisos insegura."),
                    recommendation=("Revisar el control de acceso y preferir mecanismos basados en "
                                    "msg.sender cuando corresponda."),
                ))
        return findings

    def _check_selfdestruct(self, lines, original_lines, function_map):
        findings = []
        for index, line in enumerate(lines, start=1):
            if re.search(r"\bselfdestruct\s*\(", line):
                findings.append(self._finding(
                    rule_id="SG003", title="Uso de selfdestruct", severity="MEDIUM",
                    category="Operación sensible", line=index, original_lines=original_lines,
                    function_map=function_map,
                    description=("Se detectó selfdestruct. Es una operación sensible cuyo uso "
                                 "requiere revisar permisos y comportamiento esperado."),
                    recommendation=("Confirmar que la operación sea necesaria y que su ejecución "
                                    "esté restringida correctamente."),
                ))
        return findings

    def _check_possible_reentrancy(self, lines, original_lines, function_map):
        findings = []
        external_call = re.compile(r"\.call\s*\{\s*value\s*:")
        state_update = re.compile(
            r"(?:balance|balances\s*\[[^\]]+\]|withdrawn|amount|credit|credits\s*\[[^\]]+\])\s*(?:=|-=|\+=)"
        )
        for zero_index, line in enumerate(lines):
            if not external_call.search(line):
                continue
            line_number = zero_index + 1
            current_function = function_map.get(line_number)
            window = []
            for next_index in range(zero_index + 1, min(zero_index + 7, len(lines))):
                if function_map.get(next_index + 1) != current_function:
                    break
                window.append(lines[next_index])
            if any(state_update.search(candidate) for candidate in window):
                findings.append(self._finding(
                    rule_id="SG004", title="Posible patrón de reentrancy", severity="HIGH",
                    category="Llamadas externas", line=line_number, original_lines=original_lines,
                    function_map=function_map,
                    description=("Se detectó una llamada externa con transferencia de valor antes "
                                 "de una actualización cercana del estado interno."),
                    recommendation=("Revisar el orden de las operaciones y aplicar el patrón de "
                                    "actualizar estado antes de llamadas externas cuando corresponda."),
                ))
        return findings

    def _check_unchecked_low_level_call(self, lines, original_lines, function_map):
        findings = []
        call_pattern = re.compile(r"\.call(?:\s*\{|\s*\()")
        for index, line in enumerate(lines, start=1):
            if not call_pattern.search(line):
                continue
            before_call = line.split(".call", 1)[0]
            # Si el retorno se asigna a una variable/tupla, asumimos que al menos se conserva.
            if "=" in before_call:
                continue
            findings.append(self._finding(
                rule_id="SG005", title="Resultado de llamada de bajo nivel no verificado",
                severity="MEDIUM", category="Manejo de errores", line=index,
                original_lines=original_lines, function_map=function_map,
                description=("La llamada de bajo nivel parece ejecutarse sin conservar su valor de "
                             "retorno, por lo que un fallo podría pasar inadvertido."),
                recommendation=("Guardar el resultado de la llamada y verificar explícitamente si "
                                "la operación fue exitosa."),
            ))
        return findings

    def _check_delegatecall(self, lines, original_lines, function_map):
        findings = []
        for index, line in enumerate(lines, start=1):
            if re.search(r"\.delegatecall\s*\(", line):
                findings.append(self._finding(
                    rule_id="SG006", title="Uso de delegatecall", severity="MEDIUM",
                    category="Ejecución externa", line=index, original_lines=original_lines,
                    function_map=function_map,
                    description=("Se detectó delegatecall, que ejecuta lógica externa utilizando el "
                                 "contexto de almacenamiento del contrato actual."),
                    recommendation=("Revisar cuidadosamente la dirección objetivo, permisos, layout "
                                    "de almacenamiento y origen del código ejecutado."),
                ))
        return findings

    def _check_timestamp_dependency(self, lines, original_lines, function_map):
        findings = []
        condition_pattern = re.compile(r"\b(?:if|require)\s*\(")
        for index, line in enumerate(lines, start=1):
            uses_time = "block.timestamp" in line or re.search(r"\bnow\b", line)
            if uses_time and condition_pattern.search(line):
                findings.append(self._finding(
                    rule_id="SG007", title="Dependencia temporal con block.timestamp", severity="LOW",
                    category="Lógica temporal", line=index, original_lines=original_lines,
                    function_map=function_map,
                    description=("Se detectó una condición que depende directamente del tiempo del bloque. "
                                 "Esto puede ser relevante en lógica sensible a límites temporales exactos."),
                    recommendation=("Revisar si pequeñas variaciones temporales pueden afectar el resultado "
                                    "y evitar usar el timestamp como fuente de precisión estricta."),
                ))
        return findings

    def _check_weak_randomness(self, lines, original_lines, function_map):
        findings = []
        randomness_sources = re.compile(r"block\.timestamp|blockhash\s*\(|block\.prevrandao")
        for zero_index, line in enumerate(lines):
            if "keccak256" not in line:
                continue
            window = " ".join(lines[zero_index : min(zero_index + 5, len(lines))])
            if randomness_sources.search(window):
                line_number = zero_index + 1
                findings.append(self._finding(
                    rule_id="SG008", title="Aleatoriedad basada en variables de bloque", severity="MEDIUM",
                    category="Aleatoriedad", line=line_number, original_lines=original_lines,
                    function_map=function_map,
                    description=("Se detectó una construcción de aleatoriedad que utiliza variables del "
                                 "bloque. En escenarios sensibles, estas fuentes no deben asumirse impredecibles."),
                    recommendation=("Revisar el modelo de aleatoriedad y utilizar una fuente diseñada para "
                                    "ser verificable o resistente a manipulación cuando el caso lo requiera."),
                ))
        return findings
