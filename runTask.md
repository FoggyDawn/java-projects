

### 使用说明

1. **配置文件结构**：
   ```bash
   projects_root/
   ├── project_alpha/
   │   ├── analysis-config.yml  # 对应analyze任务的配置
   │   └── analysis-log
   │       └──run_20240619-1435.log
   ├── project_beta/
   │   ├── report-options.yaml  # 对应report任务的配置
   │   └── report-log
   │       └──run_20240619-1437.log
   ```

2. **执行预设任务**：
   ```bash
   # 使用预配置任务（自动关联配置文件名）
   python runner.py \
     --java-version 11 \
     --task analyze \
     --root ./projects
   ```

3. **自定义任务执行**：
   ```bash
   # 手动指定JAR和配置（不使用预设）
   python runner.py \
     --java /custom/jdk17/bin/java \
     --jar /path/to/app.jar \
     --config custom-config.yml \
     --root ./projects
   ```
---

### 使用示例

1. **使用预设工作目录**
   ```bash
   python runner.py \
     --java-version 11 \
     --task process \
     --root ./projects
   ```
   ```text
   [Task Info]
   Project Dir: /projects/exp01
   Work Dir: /data/processing
   ```

2. **临时覆盖工作目录**
   ```bash
   python runner.py \
     --task process \
     --work-dir /tmp/processing \
     --root ./projects
   ```
   ```text
   [Task Info]
   Project Dir: /projects/exp01
   Work Dir: /tmp/processing
   ```

3. **使用项目目录作为工作目录**
   ```bash
   python runner.py \
     --task analyze \
     --root ./projects
   ```
   ```text
   [Task Info]
   Project Dir: /projects/exp02
   Work Dir: /projects/exp02
   ```

---
