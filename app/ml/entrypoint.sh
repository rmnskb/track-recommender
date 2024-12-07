MODEL_FILE="kdt.pkl"

if [ ! -f "$MODEL_FILE" ]; then
	echo "Model file does not exist, training a new one"
	python recommender.py
else
	echo "Model file exists. Skipping the training"
fi

# start the Dockerfile main process
exec "$@"
