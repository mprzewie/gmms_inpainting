# 2021-04-04 05:13:56.543162
python train_wae.py --experiment_name=wae_8_8_v3/dmfa_comp_cnv --inpainter_type=dmfa --inpainter_path ../results/inpainting/mnist/complete_data/v1/ --dataset mnist --num_epochs=10 --render_every 2 --wae_fc 8 --wae_lc 8 --dataset_root /home/mprzewiezlikowski/uj/.data --max_benchmark_batches=-1 --lr=4e-3 --batch_size=128 --convar_type naive
