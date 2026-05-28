```markdown
# 🔴 APUNTES CRÍTICOS PARA EL EXAMEN - SIN GUI

Guía de estudio para el examen de **Virtualización y Procesamiento Distribuido (VPD)** - ULPGC

## Tabla de Contenidos

1. [Condiciones del Examen](#condiciones-del-examen)
2. [Conexión SSH](#conexión-ssh-al-anfitrión)
3. [Editores: Nano vs Vi](#edición-de-ficheros-sin-gui)
4. [Acceso a MVs](#acceso-a-máquinas-virtuales-sin-gui)
5. [Prácticas](#prácticas)
6. [Checklist](#checklist-antes-del-examen)

---

## ⚠️ CONDICIONES DEL EXAMEN

### NO HABRÁ:
- ❌ Entorno gráfico (GNOME, gedit, virt-manager)
- ❌ Navegador web
- ❌ Interfaz visual de ningún tipo

### SOLO DISPONIBLE:
- ✅ Terminal SSH desde tu máquina
- ✅ Editores de texto: `nano` o `vi`
- ✅ Línea de comandos pura

---

## 🚀 Conexión SSH al Anfitrión

### Comando base:
```bash
ssh root@identificador_pc.vpd.com
# O con IP directa:
ssh root@192.168.x.x
```

### Una vez conectado por SSH:
- Todos los comandos `virsh`, `virt-install`, etc. se ejecutan IGUAL
- Acceso a consola de MVs: `virsh console mvp1`
- Edición de ficheros: `nano` o `vi`

---

## 📝 EDICIÓN DE FICHEROS SIN GUI

### NANO (RECOMENDADO PARA EXAMEN)

```bash
nano /ruta/fichero
```

#### Atajos CRÍTICOS:

| Atajo | Función |
|-------|---------|
| `Ctrl+O` | Guardar (después pulsa Enter) |
| `Ctrl+X` | Salir |
| `Ctrl+W` | Buscar texto |
| `Ctrl+K` | Cortar línea completa |
| `Ctrl+U` | Pegar |
| `Ctrl+A` | Ir al inicio de línea |
| `Ctrl+E` | Ir al final de línea |
| `Alt+/` | Ir al final del fichero |

#### Ejemplo práctico:
```bash
# Editar fstab para añadir montaje persistente
nano /etc/fstab

# Dentro de nano:
# 1. Bajar al final: Alt+/
# 2. Añadir línea nueva
# 3. Escribir: UUID=xxxx /PUNTO_MONTAJE xfs defaults 0 0
# 4. Guardar: Ctrl+O → Enter
# 5. Salir: Ctrl+X
```

---

### VI/VIM (ALTERNATIVA)

```bash
vi /ruta/fichero
```

#### Atajos CRÍTICOS:

| Atajo | Función |
|-------|---------|
| `i` | Entrar en modo INSERTAR |
| `Esc` | Salir de modo insertar |
| `:wq` | Guardar y salir |
| `:q!` | Salir SIN guardar |
| `/texto` | Buscar "texto" |
| `n` | Siguiente coincidencia |
| `dd` | Borrar línea completa |
| `:%s/viejo/nuevo/g` | Reemplazar todo |
| `:set number` | Mostrar números de línea |

#### Flujo típico:
```bash
vi /etc/fstab

# 1. Pulsar: i (modo insertar)
# 2. Escribir la línea
# 3. Pulsar: Esc (salir insertar)
# 4. Escribir: :wq
# 5. Pulsar: Enter (guardar y cerrar)
```

---

## 🖥️ ACCESO A MÁQUINAS VIRTUALES SIN GUI

### Opción 1: Consola serie virsh (RECOMENDADO)

```bash
# Desde el anfitrión (SSH)
virsh console mvp1

# Dentro de la MV:
# - Ejecutar comandos normalmente
# - SALIR: Ctrl+] (corchete cerrado)

# Ejemplo:
virsh console mvp1
dnf update -y
hostnamectl set-hostname mvp1.vpd.com
Ctrl+]  # salir
```

**Ventaja:** No necesitas saber la IP de la MV

### Opción 2: SSH a la MV (SI TIENES IP)

```bash
# Primero, obtener IP desde el anfitrión:
virsh domifaddr mvp1
# Responde: 192.168.140.2 (o la que corresponda)

# Luego, SSH directo a la MV:
ssh root@192.168.140.2

# O si tienes resolución DNS configurada:
ssh root@mvp1.vpd.com
```

---

## 🔌 FLUJO TÍPICO DE TRABAJO EN EXAMEN

### ESCENARIO: Crear y configurar mvp3 con almacenamiento

```bash
# 1. CONECTAR AL ANFITRIÓN POR SSH
ssh root@lq-d15.vpd.com

# 2. CLONAR mvp1 a mvp3
virt-clone --original mvp1 --name mvp3 --auto-clone
virsh start mvp3

# 3. CONECTAR A mvp3 POR CONSOLA SERIE
virsh console mvp3
# ↓ DENTRO DE mvp3:

# 4. CREAR PUNTO DE MONTAJE
mkdir -p /mnt/vol1

# 5. EDITAR FSTAB CON NANO
nano /etc/fstab
# Pulsar: Ctrl+O → Enter → Ctrl+X

# 6. APLICAR CAMBIOS
mount -a
df -hT

# 7. SALIR DE LA CONSOLA
Ctrl+]
# ↓ DE VUELTA EN EL ANFITRIÓN

# 8. VERIFICAR DESDE EL ANFITRIÓN
virsh domifaddr mvp3
```

---

## 📋 EDITANDO FICHEROS CRÍTICOS CON NANO

### 1. /etc/fstab (montajes persistentes)

```bash
nano /etc/fstab
```

**Contenido a añadir:**
```
UUID=abc123def456 /var/lib/libvirt/images xfs defaults 0 0
UUID=xyz789uvw    /PUNTO_MONTAJE xfs defaults 0 0
```

### 2. /etc/hosts (resolución DNS local)

```bash
nano /etc/hosts
```

**Contenido a añadir (al final):**
```
10.22.122.10  almacenamiento1.vpd.com
10.22.122.11  almacenamiento2.vpd.com
10.22.132.12  nodo1.vpd.com
10.22.132.13  nodo2.vpd.com
```

### 3. /etc/default/grub (consola serie)

```bash
nano /etc/default/grub
```

**Buscar la línea:**
```
GRUB_CMDLINE_LINUX="..."
```

**Modificar a:**
```
GRUB_CMDLINE_LINUX="console=ttyS0"
```

**Aplicar cambios:**
```bash
grub2-editenv - unset kernelopts
grub2-mkconfig -o /boot/grub2/grub.cfg
reboot
```

### 4. /etc/lvm/lvm.conf (clúster P7)

```bash
nano /etc/lvm/lvm.conf
```

**Buscar y modificar:**
```
# Antes:
# volume_list = [ ]

# Después:
volume_list = [ "fedora" ]
```

### 5. /etc/iscsi/initiatorname.iscsi (P6)

```bash
nano /etc/iscsi/initiatorname.iscsi
```

**Cambiar:**
```
InitiatorName=iqn.1993-08.org.debian:01.1234567890ab
```

**Por:**
```
InitiatorName=iqn.2026-04.com.vpd:nodo1
```

---

## 🔄 FLUJO COMPLETO: CREAR RED CON NANO

### P5 — Red NAT (Cluster)

```bash
# 1. Crear fichero XML en el anfitrión
nano red_cluster.xml
```

**Pegue este contenido en nano:**
```xml
<network>
  <name>Cluster</name>
  <forward mode='nat'/>
  <bridge name='virbr1' stp='on' delay='0'/>
  <ip address='192.168.140.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.140.2' end='192.168.140.149'/>
    </dhcp>
  </ip>
</network>
```

**En nano:** `Ctrl+O → Enter → Ctrl+X`

**Luego en terminal:**
```bash
virsh net-define red_cluster.xml
virsh net-start Cluster
virsh net-autostart Cluster
```

### P5 — Red Aislada (Almacenamiento)

```bash
nano red_almacenamiento.xml
```

**Contenido:**
```xml
<network>
  <name>Almacenamiento</name>
  <bridge name='virbr2' stp='on' delay='0'/>
  <domain name='vpd.com'/>
  <ip address='10.22.122.1' netmask='255.255.255.0'/>
</network>
```

---

## 🎯 COMANDOS QUE NO NECESITAN GUI

**TODO en el examen se hace con:**

```bash
# INFORMACIÓN
virsh list --all
virsh pool-list --all
virsh net-list --all
virsh domifaddr mvp1
virsh dominfo mvp1
virsh dumpxml mvp1

# CREACIÓN
virt-install --name mvp1 --ram 2048 ...
virt-clone --original mvp1 --name mvp2 --auto-clone

# EDICIÓN SEGURA
EDITOR=nano virsh edit mvp1    # editar XML de MV
EDITOR=nano virsh net-edit RED # editar XML de red

# ALMACENAMIENTO
virsh vol-create-as default VOL1 1G --format raw
virsh attach-disk mvp1 /ruta/vol.img sda --persistent
virsh pool-define-as NOMBRE netfs --source-host ... --target ...

# RED
virsh attach-interface mvp1 network RED --model virtio --config --live
virsh detach-interface mvp1 network --config

# CLÚSTER
pcs status
pcs resource create RECURSO ocf:heartbeat:AGENTE param1=valor1
pcs node standby nodo1.vpd.com

# FICHEROS EN MV
nano /etc/fstab
vi /etc/hosts
cat /ruta/fichero

# MONTAJES
mount -a
df -hT
blkid /dev/DISPOSITIVO
```

---

## 🚨 ERRORES FRECUENTES SIN GUI

| Error | Causa | Solución |
|-------|-------|----------|
| `Cannot connect to QEMU session` | SSH a MV sin ruta | Usar `virsh console` desde anfitrión |
| `XML file not found` | Typo en ruta | Usar `virsh edit` en lugar de ficheros directos |
| Cambios en `fstab` no aplicados | Olvidó `mount -a` | Ejecutar `mount -a` después de editar |
| Consola "cuelga" en `virsh console` | Presionar Ctrl+] mal | Presionar ambas teclas: `Ctrl` y `]` simultáneamente |
| Fichero no se guardó en nano | Olvidó confirmación | Tras `Ctrl+O` SIEMPRE presionar `Enter` |

---

## ✅ CHECKLIST ANTES DEL EXAMEN

- [ ] Sé conectarme por SSH: `ssh root@ip_anfitrion`
- [ ] Puedo abrir nano: `nano /etc/fstab`
- [ ] Sé guardar en nano: `Ctrl+O → Enter → Ctrl+X`
- [ ] Sé salir de `virsh console`: `Ctrl+]`
- [ ] Entiendo que TODO es línea de comandos (sin clics)
- [ ] Tengo clara la diferencia entre editar en **anfitrión** vs **dentro de MV**
- [ ] Puedo crear ficheros XML con nano
- [ ] Entiendo los comandos `virsh` básicos

---

## 📌 RESUMEN: HERRAMIENTAS PERMITIDAS

**SSH desde tu máquina** → Anfitrión:
- `virsh` (máquinas virtuales)
- `nano` / `vi` (editar ficheros)
- `firewall-cmd` (reglas)
- `dnf` (instalar paquetes)
- `pcs` (clúster)
- `systemctl` (servicios)

**virsh console mvp1** → Dentro de MV:
- `nano` / `vi`
- `nmcli` (red)
- `mount` (almacenamiento)
- `dnf` (instalar)
- `Ctrl+]` para SALIR

**TODO se hace sin GUI. Practica con nano y vi antes del examen.**

---

## 📚 Referencias rápidas

- [P1 - KVM](#) (próximamente)
- [P2 - Operaciones MVs](#) (próximamente)
- [P3 - Almacenamiento virtual](#) (próximamente)
- [P4 - Migración](#) (próximamente)
- [P5 - Redes virtuales](#) (próximamente)
- [P6 - iSCSI + LVM](#) (próximamente)
- [P7 - Clúster Pacemaker](#) (próximamente)

---

**Última actualización:** 2025
**Autor:** Javier Bolívar
**Universidad:** ULPGC - Grado en Ciencia e Ingeniería de Datos
```

---

## 🎯 Cómo guardarlo:

1. **Abre un editor** (VS Code, notepad++, etc.)
2. **Copia el contenido de arriba**
3. **Guárdalo como:** `README.md`
4. **Sube a GitHub/GitLab** si quieres compartirlo

---

## ✨ Mejoras opcionales:

Si quieres hacerlo aún más profesional:

```bash
# Crear tabla de contenidos automática con GitHub
# GitHub genera índice automáticamente desde los #

# Añadir badges
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with ❤️ by Javier Bolívar](https://img.shields.io/badge/Made%20with%20%E2%9D%A4%EF%B8%8F%20by-Javier%20Bol%C3%ADvar-blue)](https://github.com)
```

¿Necesitas que te ayude a subirlo a GitHub o que le añada más secciones?
