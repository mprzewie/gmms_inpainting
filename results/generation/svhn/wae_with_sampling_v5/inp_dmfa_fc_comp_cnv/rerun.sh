# 2021-04-09 08:08:24.907531
python train_wae.py --experiment_name=wae_with_sampling_v5/inp_dmfa_fc_comp_cnv --inpainter_type=dmfa --inpainter_path ../results/inpainting/svhn/fullconv/complete_data/dmfa_mse_10_eps/ --batch_size 64 --dataset svhn --img_size 32 --mask_hidden_h 16 --mask_hidden_w 16 --num_epochs=10 --render_every 2 --dataset_root /mnt/users/mprzewiezlikowski/local/data/.data/ --lr 4e-4 --wae_bl 2 --wae_recon_loss mse --max_benchmark_batches=-1 --convar_type naive
