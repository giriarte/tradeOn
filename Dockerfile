FROM public.ecr.aws/lambda/python:3.13

# Copy the requirements.txt file (must be in the same directory as Dockerfile)
COPY requirements.txt .

# Install all dependencies from requirements.txt, including yfinance, llvmlite, etc.
# The dependencies are installed into the standard /var/task location
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your application code into the image
# (StrategyMonitorLambda.py and any other local code files)
COPY . /var/task

# Set the command that executes when the container starts.
# Format: [filename].[handler_function]
CMD ["StrategyMonitorLambda.invoke"]