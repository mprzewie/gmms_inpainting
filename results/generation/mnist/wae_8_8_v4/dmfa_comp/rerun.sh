# 2021-04-08 16:30:12.844392
python train_wae.py --experiment_name=wae_8_8_v4/dmfa_comp --inpainter_type=dmfa --inpainter_path ../results/inpainting/mnist/complete_data/v1/ --dataset mnist --num_epochs=10 --render_every 2 --wae_fc 8 --wae_lc 8 --dataset_root /home/mprzewiezlikowski/uj/.data --max_benchmark_batches=-1 --lr=4e-3 --batch_size=128
